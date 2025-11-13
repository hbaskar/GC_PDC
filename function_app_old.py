import azure.functions as func
import logging

# Import blueprints
from blueprints.classifications import bp as classifications_bp
from blueprints.lookups import bp as lookups_bp  
from blueprints.health import bp as health_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Register blueprints
app.register_blueprint(classifications_bp)
app.register_blueprint(lookups_bp)
app.register_blueprint(health_bp)

@app.route(route="classifications", methods=["GET"])
def get_classifications(req: func.HttpRequest) -> func.HttpResponse:
    """Get all PDC Classifications with optional filtering and pagination."""
    try:
        # Parse query parameters
        page = int(req.params.get('page', '1'))
        size = int(req.params.get('size', '20'))
        is_active = req.params.get('is_active')
        classification_level = req.params.get('classification_level')
        organization_id = req.params.get('organization_id')
        sensitivity_rating = req.params.get('sensitivity_rating')
        media_type = req.params.get('media_type')
        file_type = req.params.get('file_type')
        search = req.params.get('search')
        include_deleted = req.params.get('include_deleted', 'false').lower() == 'true'
        
        # Convert parameters to appropriate types
        if is_active is not None:
            is_active = is_active.lower() == 'true'
        
        if organization_id:
            organization_id = int(organization_id)
        
        if sensitivity_rating:
            sensitivity_rating = int(sensitivity_rating)
        
        # Calculate skip
        skip = (page - 1) * size
        
        # Get database session and perform query
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        classifications, total = crud.get_all(
            skip=skip,
            limit=size,
            is_active=is_active,
            classification_level=classification_level,
            organization_id=organization_id,
            sensitivity_rating=sensitivity_rating,
            media_type=media_type,
            file_type=file_type,
            search=search,
            include_deleted=include_deleted
        )
        
        # Convert to response format
        classification_responses = [
            PDCClassificationResponse.model_validate(classification).model_dump()
            for classification in classifications
        ]
        
        # Calculate pagination info
        pages = math.ceil(total / size) if total > 0 else 1
        
        response_data = PDCClassificationList(
            items=classification_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        ).model_dump()
        
        return create_success_response(response_data)
        
    except ValueError as e:
        return create_error_response("Invalid query parameters", 400, str(e))
    except Exception as e:
        logging.error(f"Error getting classifications: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/{classification_id:int}", methods=["GET"])
def get_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific PDC Classification by ID."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        classification = crud.get_by_id(classification_id)
        if not classification:
            return create_error_response("Classification not found", 404)
        
        response_data = PDCClassificationResponse.model_validate(classification).model_dump()
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Error getting classification {classification_id}: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications", methods=["POST"])
def create_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new PDC Classification."""
    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_error_response("Invalid JSON in request body", 400)
        
        if not req_body:
            return create_error_response("Request body is required", 400)
        
        # Validate request data
        try:
            classification_data = PDCClassificationCreate(**req_body)
        except ValidationError as e:
            return create_error_response("Validation error", 400, str(e))
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        # Check if code already exists
        existing_classification = crud.get_by_code(classification_data.code)
        if existing_classification:
            return create_error_response("Classification with this code already exists", 409)
        
        # Create classification
        new_classification = crud.create(classification_data)
        response_data = PDCClassificationResponse.model_validate(new_classification).model_dump()
        
        return create_success_response(response_data, 201)
        
    except Exception as e:
        logging.error(f"Error creating classification: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/{classification_id:int}", methods=["PUT"])
def update_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Update a PDC Classification."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_error_response("Invalid JSON in request body", 400)
        
        if not req_body:
            return create_error_response("Request body is required", 400)
        
        # Validate request data
        try:
            classification_data = PDCClassificationUpdate(**req_body)
        except ValidationError as e:
            return create_error_response("Validation error", 400, str(e))
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        # Check if code already exists (if updating code)
        if classification_data.code:
            existing_classification = crud.get_by_code(classification_data.code)
            if existing_classification and existing_classification.classification_id != classification_id:
                return create_error_response("Classification with this code already exists", 409)
        
        # Update classification
        updated_classification = crud.update(classification_id, classification_data)
        if not updated_classification:
            return create_error_response("Classification not found", 404)
        
        response_data = PDCClassificationResponse.model_validate(updated_classification).model_dump()
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Error updating classification {classification_id}: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/{classification_id:int}", methods=["DELETE"])
def delete_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a PDC Classification."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        soft_delete = req.params.get('soft', 'true').lower() == 'true'
        deleted_by = req.params.get('deleted_by')
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        if soft_delete:
            # Soft delete (set is_deleted = True)
            updated_classification = crud.soft_delete(classification_id, deleted_by)
            if not updated_classification:
                return create_error_response("Classification not found", 404)
            
            response_data = PDCClassificationResponse.model_validate(updated_classification).model_dump()
            return create_success_response(response_data)
        else:
            # Hard delete
            success = crud.delete(classification_id)
            if not success:
                return create_error_response("Classification not found", 404)
            
            return create_success_response({"message": "Classification deleted successfully"})
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Error deleting classification {classification_id}: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/{classification_id:int}/restore", methods=["POST"])
def restore_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Restore a soft-deleted PDC Classification."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Parse request body for restored_by
        restored_by = None
        try:
            req_body = req.get_json()
            if req_body:
                restored_by = req_body.get('restored_by')
        except ValueError:
            pass  # Body is optional for this endpoint
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        # Restore classification
        restored_classification = crud.restore(classification_id, restored_by)
        if not restored_classification:
            return create_error_response("Classification not found or not deleted", 404)
        
        response_data = PDCClassificationResponse.model_validate(restored_classification).model_dump()
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Error restoring classification {classification_id}: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/{classification_id:int}/access", methods=["POST"])
def track_classification_access(req: func.HttpRequest) -> func.HttpResponse:
    """Track access to a PDC Classification."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_error_response("Invalid JSON in request body", 400)
        
        if not req_body or 'accessed_by' not in req_body:
            return create_error_response("'accessed_by' field is required", 400)
        
        accessed_by = req_body.get('accessed_by')
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        # Update last accessed information
        updated_classification = crud.update_last_accessed(classification_id, accessed_by)
        if not updated_classification:
            return create_error_response("Classification not found", 404)
        
        return create_success_response({
            "classification_id": classification_id,
            "last_accessed_at": updated_classification.last_accessed_at.isoformat() if updated_classification.last_accessed_at else None,
            "last_accessed_by": updated_classification.last_accessed_by
        })
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Error tracking access for classification {classification_id}: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/metadata", methods=["GET"])
def get_classification_metadata(req: func.HttpRequest) -> func.HttpResponse:
    """Get classification metadata (levels, media types, file types, series)."""
    try:
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        metadata = {
            "classification_levels": crud.get_classification_levels(),
            "media_types": crud.get_media_types(),
            "file_types": crud.get_file_types(),
            "series": crud.get_series()
        }
        
        return create_success_response(metadata)
        
    except Exception as e:
        logging.error(f"Error getting classification metadata: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/organization/{organization_id:int}", methods=["GET"])
def get_classifications_by_organization(req: func.HttpRequest) -> func.HttpResponse:
    """Get all classifications for a specific organization."""
    try:
        organization_id = int(req.route_params.get('organization_id'))
        is_active = req.params.get('is_active')
        
        # Convert is_active to boolean if provided
        if is_active is not None:
            is_active = is_active.lower() == 'true'
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        classifications = crud.get_by_organization(organization_id, is_active)
        
        # Convert to summary format for better performance
        from schemas.classification_schemas import PDCClassificationSummary
        classification_responses = [
            PDCClassificationSummary.model_validate(classification).model_dump()
            for classification in classifications
        ]
        
        return create_success_response({
            "organization_id": organization_id,
            "classifications": classification_responses,
            "count": len(classification_responses)
        })
        
    except ValueError:
        return create_error_response("Invalid organization ID", 400)
    except Exception as e:
        logging.error(f"Error getting classifications for organization {organization_id}: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="classifications/sensitivity/{min_rating:int}", methods=["GET"])
def get_classifications_by_sensitivity(req: func.HttpRequest) -> func.HttpResponse:
    """Get classifications by sensitivity rating."""
    try:
        min_rating = int(req.route_params.get('min_rating'))
        max_rating = req.params.get('max_rating')
        
        if max_rating:
            max_rating = int(max_rating)
        
        # Get database session
        db = next(get_db())
        crud = PDCClassificationCRUD(db)
        
        classifications = crud.get_by_sensitivity_rating(min_rating, max_rating)
        
        # Convert to summary format
        from schemas.classification_schemas import PDCClassificationSummary
        classification_responses = [
            PDCClassificationSummary.model_validate(classification).model_dump()
            for classification in classifications
        ]
        
        return create_success_response({
            "min_rating": min_rating,
            "max_rating": max_rating,
            "classifications": classification_responses,
            "count": len(classification_responses)
        })
        
    except ValueError:
        return create_error_response("Invalid sensitivity rating", 400)
    except Exception as e:
        logging.error(f"Error getting classifications by sensitivity: {str(e)}")
        return create_error_response("Internal server error", 500, str(e))

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    try:
        # Test database connection
        from sqlalchemy import text
        from datetime import datetime
        db = next(get_db())
        db.execute(text("SELECT 1"))
        
        return create_success_response({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return create_error_response("Service unhealthy", 503, str(e))

@app.route(route="diagnostic", methods=["GET"])
def diagnostic_check(req: func.HttpRequest) -> func.HttpResponse:
    """Diagnostic endpoint to debug configuration issues."""
    try:
        diagnostic_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment_variables": {
                "AZURE_SQL_AUTH_METHOD": os.environ.get('AZURE_SQL_AUTH_METHOD', 'NOT SET'),
                "AZURE_SQL_SERVER": os.environ.get('AZURE_SQL_SERVER', 'NOT SET'),
                "AZURE_SQL_DATABASE": os.environ.get('AZURE_SQL_DATABASE', 'NOT SET'),
                "AZURE_SQL_DRIVER": os.environ.get('AZURE_SQL_DRIVER', 'NOT SET'),
                "AZURE_SQL_PORT": os.environ.get('AZURE_SQL_PORT', 'NOT SET'),
                "AZURE_SQL_MANAGED_IDENTITY_CLIENT_ID": os.environ.get('AZURE_SQL_MANAGED_IDENTITY_CLIENT_ID', 'NOT SET'),
                
                # Check if any old variables are still set
                "AZURE_SQL_USERNAME": "SET" if os.environ.get('AZURE_SQL_USERNAME') else 'NOT SET',
                "AZURE_SQL_PASSWORD": "SET" if os.environ.get('AZURE_SQL_PASSWORD') else 'NOT SET',
                "AZURE_SQL_AUTHENTICATION": os.environ.get('AZURE_SQL_AUTHENTICATION', 'NOT SET'),
            },
            "database_config": None,
            "engine_info": None,
            "connection_test": None
        }
        
        # Test database configuration creation
        try:
            # Clear any cached config first
            import database.config
            database.config._db_config = None
            database.config._engine = None
            database.config._SessionLocal = None
            
            from database.config import DatabaseConfig
            config = DatabaseConfig()
            
            diagnostic_info["database_config"] = {
                "auth_method": config.auth_method,
                "server": config.server,
                "database": config.database,
                "driver": config.driver,
                "managed_identity_client_id": config.managed_identity_client_id,
                "port": config.port,
            }
            
            # Test connection string generation
            connection_string = config.get_connection_string()
            diagnostic_info["database_config"]["connection_string"] = connection_string
            
            # Check engine creation logic
            sql_condition = (config.auth_method == 'sql' and getattr(config, 'authentication', None) == 'ActiveDirectoryPassword')
            mi_condition = (config.auth_method == 'managed_identity')
            combined_condition = sql_condition or mi_condition
            
            diagnostic_info["engine_info"] = {
                "sql_condition": sql_condition,
                "mi_condition": mi_condition,
                "combined_condition": combined_condition,
                "will_use_custom_creator": combined_condition
            }
            
        except Exception as e:
            diagnostic_info["database_config"] = f"ERROR: {str(e)}"
            logging.error(f"Database config creation failed: {str(e)}")
        
        # Test actual engine creation
        try:
            from database.config import get_engine
            
            engine = get_engine()
            has_custom_creator = hasattr(engine.pool, '_creator')
            
            diagnostic_info["engine_info"] = {
                **diagnostic_info.get("engine_info", {}),
                "engine_type": str(type(engine)),
                "has_custom_creator": has_custom_creator,
            }
            
        except Exception as e:
            diagnostic_info["engine_info"] = {
                **diagnostic_info.get("engine_info", {}),
                "engine_creation_error": str(e)
            }
            logging.error(f"Engine creation failed: {str(e)}")
        
        return create_success_response(diagnostic_info)
        
    except Exception as e:
        logging.error(f"Diagnostic endpoint failed: {str(e)}")
        return create_error_response("Diagnostic failed", 500, str(e))

# ========== LOOKUP API ENDPOINTS ==========

@app.route(route="lookups/types", methods=["GET"])
def get_lookup_types(req: func.HttpRequest) -> func.HttpResponse:
    """Get all lookup types with optional filtering."""
    try:
        # Parse query parameters
        page = int(req.params.get('page', 1))
        size = int(req.params.get('size', 50))
        active_only = req.params.get('active_only', 'true').lower() == 'true'
        include_counts = req.params.get('include_counts', 'false').lower() == 'true'
        
        # Validate pagination
        if page < 1 or size < 1 or size > 100:
            return create_error_response("Invalid pagination parameters", 400)
        
        # Get database connection and service
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Get lookup types
        lookup_types = lookup_service.get_all_lookup_types(
            active_only=active_only, 
            skip=(page - 1) * size, 
            limit=size
        )
        
        total = lookup_service.count_lookup_types(active_only=active_only)
        
        # Convert to response format
        if include_counts:
            # Include code counts for each type
            items = []
            for lookup_type in lookup_types:
                type_data = PDCLookupTypeSummary.model_validate(lookup_type).model_dump()
                type_data['code_count'] = lookup_service.count_lookup_codes_by_type(
                    lookup_type.lookup_type, active_only=True
                )
                items.append(type_data)
        else:
            items = [
                PDCLookupTypeResponse.model_validate(lookup_type).model_dump()
                for lookup_type in lookup_types
            ]
        
        # Create paginated response
        pages = math.ceil(total / size) if size > 0 else 0
        response_data = {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
        
        return create_success_response(response_data)
        
    except Exception as e:
        logging.error(f"Get lookup types failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup types", 500, str(e))

@app.route(route="lookups/types/{lookup_type}", methods=["GET"])  
def get_lookup_type(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific lookup type with optional codes."""
    try:
        lookup_type = req.route_params.get('lookup_type')
        include_codes = req.params.get('include_codes', 'false').lower() == 'true'
        active_codes_only = req.params.get('active_codes_only', 'true').lower() == 'true'
        
        if not lookup_type:
            return create_error_response("Lookup type is required", 400)
        
        # Get database connection and service
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Get lookup type
        db_lookup_type = lookup_service.get_lookup_type(lookup_type)
        if not db_lookup_type:
            return create_error_response("Lookup type not found", 404)
        
        if include_codes:
            # Get codes for this type
            codes = lookup_service.get_lookup_codes_by_type(
                lookup_type, 
                active_only=active_codes_only
            )
            
            response_data = PDCLookupTypeResponse.model_validate(db_lookup_type).model_dump()
            response_data['lookup_codes'] = [
                PDCLookupCodeResponse.model_validate(code).model_dump()
                for code in codes
            ]
        else:
            response_data = PDCLookupTypeResponse.model_validate(db_lookup_type).model_dump()
        
        return create_success_response(response_data)
        
    except Exception as e:
        logging.error(f"Get lookup type failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup type", 500, str(e))

@app.route(route="lookups/codes/{lookup_type}", methods=["GET"])
def get_lookup_codes_by_type(req: func.HttpRequest) -> func.HttpResponse:
    """Get all lookup codes for a specific type."""
    try:
        lookup_type = req.route_params.get('lookup_type')
        page = int(req.params.get('page', 1))
        size = int(req.params.get('size', 100))  # Higher default for codes
        active_only = req.params.get('active_only', 'true').lower() == 'true'
        
        if not lookup_type:
            return create_error_response("Lookup type is required", 400)
        
        # Validate pagination
        if page < 1 or size < 1 or size > 200:
            return create_error_response("Invalid pagination parameters", 400)
        
        # Get database connection and service
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Verify lookup type exists
        if not lookup_service.get_lookup_type(lookup_type):
            return create_error_response("Lookup type not found", 404)
        
        # Get lookup codes
        lookup_codes = lookup_service.get_lookup_codes_by_type(
            lookup_type,
            active_only=active_only,
            skip=(page - 1) * size,
            limit=size
        )
        
        total = lookup_service.count_lookup_codes_by_type(lookup_type, active_only=active_only)
        
        # Convert to response format
        items = [
            PDCLookupCodeResponse.model_validate(code).model_dump()
            for code in lookup_codes
        ]
        
        # Create paginated response
        pages = math.ceil(total / size) if size > 0 else 0
        response_data = {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "lookup_type": lookup_type
        }
        
        return create_success_response(response_data)
        
    except Exception as e:
        logging.error(f"Get lookup codes failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))

@app.route(route="lookups/codes/{lookup_type}/{lookup_code}", methods=["GET"])
def get_lookup_code(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific lookup code."""
    try:
        lookup_type = req.route_params.get('lookup_type')
        lookup_code = req.route_params.get('lookup_code')
        
        if not lookup_type or not lookup_code:
            return create_error_response("Both lookup_type and lookup_code are required", 400)
        
        # Get database connection and service
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Get lookup code
        db_lookup_code = lookup_service.get_lookup_code(lookup_type, lookup_code)
        if not db_lookup_code:
            return create_error_response("Lookup code not found", 404)
        
        response_data = PDCLookupCodeResponse.model_validate(db_lookup_code).model_dump()
        return create_success_response(response_data)
        
    except Exception as e:
        logging.error(f"Get lookup code failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup code", 500, str(e))

@app.route(route="lookups/batch/codes", methods=["POST"])
def get_lookup_codes_batch(req: func.HttpRequest) -> func.HttpResponse:
    """Get lookup codes for multiple lookup types in a single request."""
    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_error_response("Invalid JSON in request body", 400)
        
        if not req_body:
            return create_error_response("Request body is required", 400)
        
        # Validate required fields
        lookup_types = req_body.get('lookup_types', [])
        if not lookup_types:
            return create_error_response("lookup_types array is required", 400)
        
        if not isinstance(lookup_types, list):
            return create_error_response("lookup_types must be an array", 400)
        
        if len(lookup_types) > 20:  # Reasonable limit
            return create_error_response("Maximum 20 lookup types allowed per request", 400)
        
        # Parse optional parameters
        active_only = req_body.get('active_only', True)
        include_inactive_types = req_body.get('include_inactive_types', False)
        
        # Get database connection and service
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Build response
        result = {
            "lookup_types": [],
            "requested_count": len(lookup_types),
            "found_count": 0,
            "not_found": [],
            "total_codes": 0
        }
        
        for lookup_type in lookup_types:
            # Verify lookup type exists
            db_lookup_type = lookup_service.get_lookup_type(lookup_type)
            if not db_lookup_type:
                result["not_found"].append(lookup_type)
                continue
                
            # Skip inactive types unless explicitly requested
            if not include_inactive_types and not db_lookup_type.is_active:
                result["not_found"].append(f"{lookup_type} (inactive)")
                continue
            
            # Get codes for this type
            codes = lookup_service.get_lookup_codes_by_type(
                lookup_type, 
                active_only=active_only
            )
            
            # Build type response
            type_response = {
                "lookup_type": lookup_type,
                "display_name": db_lookup_type.display_name,
                "description": db_lookup_type.description,
                "is_active": db_lookup_type.is_active,
                "codes": [
                    PDCLookupCodeResponse.model_validate(code).model_dump()
                    for code in codes
                ],
                "code_count": len(codes)
            }
            
            result["lookup_types"].append(type_response)
            result["total_codes"] += len(codes)
        
        result["found_count"] = len(result["lookup_types"])
        
        return create_success_response(result)
        
    except Exception as e:
        logging.error(f"Get lookup codes batch failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))

@app.route(route="lookups/batch/codes", methods=["GET"])
def get_lookup_codes_batch_get(req: func.HttpRequest) -> func.HttpResponse:
    """Get lookup codes for multiple lookup types via query parameters."""
    try:
        # Parse query parameters
        types_param = req.params.get('types', '')
        if not types_param:
            return create_error_response("'types' query parameter is required", 400)
        
        # Parse comma-separated lookup types
        lookup_types = [t.strip().upper() for t in types_param.split(',') if t.strip()]
        if not lookup_types:
            return create_error_response("At least one lookup type must be specified", 400)
        
        if len(lookup_types) > 20:  # Reasonable limit
            return create_error_response("Maximum 20 lookup types allowed per request", 400)
        
        # Parse optional parameters
        active_only = req.params.get('active_only', 'true').lower() == 'true'
        include_inactive_types = req.params.get('include_inactive_types', 'false').lower() == 'true'
        
        # Get database connection and service
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Build response
        result = {
            "lookup_types": [],
            "requested_count": len(lookup_types),
            "found_count": 0,
            "not_found": [],
            "total_codes": 0
        }
        
        for lookup_type in lookup_types:
            # Verify lookup type exists
            db_lookup_type = lookup_service.get_lookup_type(lookup_type)
            if not db_lookup_type:
                result["not_found"].append(lookup_type)
                continue
                
            # Skip inactive types unless explicitly requested
            if not include_inactive_types and not db_lookup_type.is_active:
                result["not_found"].append(f"{lookup_type} (inactive)")
                continue
            
            # Get codes for this type
            codes = lookup_service.get_lookup_codes_by_type(
                lookup_type, 
                active_only=active_only
            )
            
            # Build type response
            type_response = {
                "lookup_type": lookup_type,
                "display_name": db_lookup_type.display_name,
                "description": db_lookup_type.description,
                "is_active": db_lookup_type.is_active,
                "codes": [
                    PDCLookupCodeResponse.model_validate(code).model_dump()
                    for code in codes
                ],
                "code_count": len(codes)
            }
            
            result["lookup_types"].append(type_response)
            result["total_codes"] += len(codes)
        
        result["found_count"] = len(result["lookup_types"])
        
        return create_success_response(result)
        
    except Exception as e:
        logging.error(f"Get lookup codes batch (GET) failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))

@app.route(route="lookups/summary", methods=["GET"])
def get_lookup_summary(req: func.HttpRequest) -> func.HttpResponse:
    """Get summary statistics for all lookup data."""
    try:
        # Get database connection and service
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Get summary stats
        stats = lookup_service.get_lookup_stats()
        
        return create_success_response(stats)
        
    except Exception as e:
        logging.error(f"Get lookup summary failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup summary", 500, str(e))
