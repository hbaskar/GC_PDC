import logging
import azure.functions as func
from services.lookup_service import PDCLookupService
from database.config import get_db
import math
from services.lookup_service import LookupPaginationQueryParser


bp = func.Blueprint()

# --- Lookup Types CRUD ---
from schemas.classification_schemas import ErrorResponse

# Blueprint
bp = func.Blueprint()

def create_error_response(message: str, status_code: int, detail: str = None) -> func.HttpResponse:
    error_response = ErrorResponse(
        error=message,
        detail=detail,
        status_code=status_code
    )
    return func.HttpResponse(
        error_response.model_dump_json(),
        status_code=status_code,
        mimetype="application/json"
    )

def create_success_response(data: dict, status_code: int = 200) -> func.HttpResponse:
    import json
    return func.HttpResponse(
        json.dumps(data, default=str),
        status_code=status_code,
        mimetype="application/json"
    )


@bp.route(route="lookups/types", methods=["POST"])
def create_lookup_type(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new lookup type."""
    db = next(get_db())
    try:
        lookup_service = PDCLookupService(db)
        data = req.get_json()
        from schemas.lookup_schemas import PDCLookupTypeCreate
        lookup_type_obj = PDCLookupTypeCreate(**data)
        created = lookup_service.create_lookup_type(lookup_type_obj)
        return create_success_response(lookup_service.to_api_dict_type(created), status_code=201)
    except Exception as e:
        logging.error(f"Create lookup type failed: {str(e)}")
        return create_error_response("Failed to create lookup type", 500, str(e))
    finally:
        db.close()


@bp.route(route="lookups/types", methods=["PUT"])
def update_lookup_type(req: func.HttpRequest) -> func.HttpResponse:
    """Update an existing lookup type."""
    db = next(get_db())
    try:
        lookup_service = PDCLookupService(db)
        data = req.get_json()
        lookup_type = data.get('lookup_type')
        from schemas.lookup_schemas import PDCLookupTypeUpdate
        update_obj = PDCLookupTypeUpdate(**data)
        updated = lookup_service.update_lookup_type(
            lookup_type,
            display_name=update_obj.display_name,
            description=update_obj.description,
            is_active=update_obj.is_active,
            modified_by=update_obj.modified_by
        )
        if not updated:
            return create_error_response("Lookup type not found", 404)
        return create_success_response(lookup_service.to_api_dict_type(updated))
    except Exception as e:
        logging.error(f"Update lookup type failed: {str(e)}")
        return create_error_response("Failed to update lookup type", 500, str(e))
    finally:
        db.close()


@bp.route(route="lookups/types/{lookup_type}", methods=["DELETE"])
def delete_lookup_type(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a lookup type."""
    db = next(get_db())
    try:
        lookup_service = PDCLookupService(db)
        lookup_type = req.route_params.get('lookup_type')
        deleted = lookup_service.delete_lookup_type(lookup_type)
        if not deleted:
            return create_error_response("Lookup type not found", 404)
        return create_success_response({"success": True})
    except Exception as e:
        logging.error(f"Delete lookup type failed: {str(e)}")
        return create_error_response("Failed to delete lookup type", 500, str(e))
    finally:
        db.close()


@bp.route(route="lookups/types", methods=["GET"])
def get_lookup_types(req: func.HttpRequest) -> func.HttpResponse:
    """Get all lookup types with optional filtering."""
    db = next(get_db())
    try:
        # Parse query parameters
        page = int(req.params.get('page', 1))
        size = int(req.params.get('size', 50))
        include_counts = req.params.get('include_counts', 'false').lower() == 'true'
        # Robustly parse include_inactive_types from query params
        raw_inactive = req.params.get('include_inactive_types', 'false')
        if isinstance(raw_inactive, bool):
            include_inactive_types = raw_inactive
        elif isinstance(raw_inactive, str):
            include_inactive_types = raw_inactive.strip().lower() in ('true', '1', 'yes')
        else:
            include_inactive_types = False
        # Determine active_only based on include_inactive_types
        active_only = not include_inactive_types
        # Validate pagination
        if page < 1 or size < 1 or size > 100:
            return create_error_response("Invalid pagination parameters", 400)
        lookup_service = PDCLookupService(db)
        # Get lookup types
        lookup_types = lookup_service.get_all_lookup_types(
            active_only=active_only,
            skip=(page - 1) * size,
            limit=size
        )
        total = lookup_service.count_lookup_types(active_only=active_only)
        # Convert to response format using model's to_dict() method
        if include_counts:
            # Include code counts for each type
            items = []
            for lookup_type in lookup_types:
                type_data = lookup_service.to_api_dict_type(lookup_type)
                type_data['code_count'] = lookup_service.count_lookup_codes_by_type(
                    lookup_type.lookup_type, active_only=True
                )
                items.append(type_data)
        else:
            items = [lookup_service.to_api_dict_type(lookup_type) for lookup_type in lookup_types]
        # Create paginated response
        pages = math.ceil(total / size) if size > 0 else 0
        response_data = {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "include_inactive_types": include_inactive_types
        }
        return create_success_response(response_data)
    except Exception as e:
        logging.error(f"Get lookup types failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup types", 500, str(e))
    finally:
        db.close()

@bp.route(route="lookups/types/{lookup_type}", methods=["GET"])
def get_lookup_type(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific lookup type with optional codes."""
    db = next(get_db())
    try:
        lookup_type = req.route_params.get('lookup_type')
        include_codes = req.params.get('include_codes', 'false').lower() == 'true'
        active_codes_only = req.params.get('active_codes_only', 'true').lower() == 'true'
        if not lookup_type:
            return create_error_response("Lookup type is required", 400)
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
            response_data = lookup_service.to_api_dict_type(db_lookup_type)
            response_data['lookup_codes'] = [
                lookup_service.to_api_dict_code(code) for code in codes
            ]
        else:
            response_data = lookup_service.to_api_dict_type(db_lookup_type)
        return create_success_response(response_data)
    except Exception as e:
        logging.error(f"Get lookup type failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup type", 500, str(e))
    finally:
        db.close()

@bp.route(route="lookups/codes/{lookup_type}", methods=["GET"])
def get_lookup_codes_by_type(req: func.HttpRequest) -> func.HttpResponse:
    """Get all lookup codes for a specific type with advanced pagination."""
    db = next(get_db())
    try:
        lookup_type = req.route_params.get('lookup_type')
        if not lookup_type:
            return create_error_response("Lookup type is required", 400)
        # Parse query parameters for enhanced pagination
        request_params = dict(req.params)
        lookup_service = PDCLookupService(db)
        # Verify lookup type exists
        if not lookup_service.get_lookup_type(lookup_type):
            return create_error_response("Lookup type not found", 404)
        # Parse pagination parameters
        pagination = LookupPaginationQueryParser.parse_pagination_params(request_params)
        # Get search and other parameters
        search = request_params.get('search', '').strip() or None
        include_deleted = request_params.get('include_deleted', 'false').lower() in ('true', '1', 'yes')
        # Robustly parse include_inactive_types from query params
        raw_inactive = request_params.get('include_inactive_types', False)
        if isinstance(raw_inactive, bool):
            include_inactive_types = raw_inactive
        elif isinstance(raw_inactive, str):
            include_inactive_types = raw_inactive.strip().lower() in ('true', '1', 'yes')
        else:
            include_inactive_types = False
        # If include_inactive_types is set, include inactive codes
        result = lookup_service.get_by_type_paginated(
            lookup_type=lookup_type,
            pagination=pagination,
            search=search,
            include_inactive=include_inactive_types or include_deleted
        )
        # Add lookup_type to response metadata
        result['lookup_type'] = lookup_type
        return create_success_response(result)
    except Exception as e:
        logging.error(f"Get lookup codes failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))
    finally:
        db.close()

@bp.route(route="lookups/codes", methods=["GET"])
def get_all_lookup_codes(req: func.HttpRequest) -> func.HttpResponse:
    """Get all lookup codes with advanced pagination and filtering."""
    try:
        # Parse query parameters for enhanced pagination
        request_params = dict(req.params)
        # Get database connection
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        # Parse pagination parameters
        pagination = LookupPaginationQueryParser.parse_pagination_params(request_params)
        # Parse filter parameters
        filters = LookupPaginationQueryParser.parse_filter_params(request_params)
        # Get search and other parameters
        search = request_params.get('search', '').strip() or None
        include_deleted = request_params.get('include_deleted', 'false').lower() in ('true', '1', 'yes')
        # Use legacy active_only parameter if provided
        if 'active_only' in request_params and 'is_active' not in filters:
            filters['is_active'] = request_params['active_only'].lower() in ('true', '1', 'yes')
        # Get paginated results
        result = lookup_service.get_lookup_codes_paginated(
            pagination=pagination,
            filters=filters,
            search=search,
            include_inactive=include_deleted
        )
        return create_success_response(result)
    except Exception as e:
        logging.error(f"Get all lookup codes failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))



@bp.route(route="lookups/batch/codes", methods=["POST"])
def get_lookup_codes_batch(req: func.HttpRequest) -> func.HttpResponse:
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
                    active_only=not include_inactive_types
            )
            
            # Build type response using model's to_dict() method
            type_response = lookup_service.to_api_dict_type(db_lookup_type)
            type_response["codes"] = [lookup_service.to_api_dict_code(code) for code in codes]
            type_response["code_count"] = len(codes)
            
            result["lookup_types"].append(type_response)
            result["total_codes"] += len(codes)
        
        result["found_count"] = len(result["lookup_types"])
        
        return create_success_response(result)
        
    except Exception as e:
        logging.error(f"Get lookup codes batch failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))

@bp.route(route="lookups/codes", methods=["POST"])
def create_lookup_code(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new lookup code."""
    try:
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        data = req.get_json()
        from schemas.lookup_schemas import PDCLookupCodeCreate
        lookup_code_obj = PDCLookupCodeCreate(**data)
        created = lookup_service.create_lookup_code(lookup_code_obj)
        return create_success_response(lookup_service.to_api_dict_code(created), status_code=201)
    except Exception as e:
        logging.error(f"Create lookup code failed: {str(e)}")
        return create_error_response("Failed to create lookup code", 500, str(e))

@bp.route(route="lookups/codes", methods=["PUT"])
def update_lookup_code(req: func.HttpRequest) -> func.HttpResponse:
    """Update an existing lookup code."""
    try:
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        data = req.get_json()
        lookup_type = data.get('lookup_type')
        lookup_code = data.get('lookup_code')
        from schemas.lookup_schemas import PDCLookupCodeUpdate
        update_obj = PDCLookupCodeUpdate(**data)
        updated = lookup_service.update_lookup_code(
            lookup_type,
            lookup_code,
            display_name=update_obj.display_name,
            description=update_obj.description,
            is_active=update_obj.is_active,
            sort_order=update_obj.sort_order,
            modified_by=update_obj.modified_by
        )
        if not updated:
            return create_error_response("Lookup code not found", 404)
        return create_success_response(lookup_service.to_api_dict_code(updated))
    except Exception as e:
        logging.error(f"Update lookup code failed: {str(e)}")
        return create_error_response("Failed to update lookup code", 500, str(e))

@bp.route(route="lookups/codes/{lookup_type}/{lookup_code}", methods=["DELETE"])
def delete_lookup_code(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a lookup code."""
    try:
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        lookup_type = req.route_params.get('lookup_type')
        lookup_code = req.route_params.get('lookup_code')
        deleted = lookup_service.delete_lookup_code(lookup_type, lookup_code)
        if not deleted:
            return create_error_response("Lookup code not found", 404)
        return create_success_response({"success": True})
    except Exception as e:
        logging.error(f"Delete lookup code failed: {str(e)}")
        return create_error_response("Failed to delete lookup code", 500, str(e))

@bp.route(route="lookups/batch/codes/cursor", methods=["POST"])
def get_lookup_codes_batch_cursor_paginated(req: func.HttpRequest) -> func.HttpResponse:

    # Parse request body with improved error handling
    try:
        req_body = req.get_json()
        logging.info(f"Batch cursor pagination - Parsed request body: {req_body}")
    except ValueError as ve:
        logging.error(f"Batch cursor pagination - JSON parsing error: {str(ve)}")
        try:
            raw_body = req.get_body().decode('utf-8')
            logging.error(f"Batch cursor pagination - Raw request body: {raw_body}")
        except Exception as raw_error:
            logging.error(f"Batch cursor pagination - Could not decode raw body: {str(raw_error)}")
        return create_error_response("Invalid JSON in request body", 400, f"JSON parse error: {str(ve)}")
    except Exception as e:
        logging.error(f"Batch cursor pagination - Unexpected error parsing JSON: {str(e)}")
        return create_error_response("Error parsing request body", 400, str(e))

    if not req_body:
        return create_error_response("Request body is required", 400)

    # Log the content type for debugging
    content_type = req.headers.get('content-type', 'Not specified')
    logging.info(f"Batch cursor pagination - Content-Type: {content_type}")

    # Validate request body structure
    if not isinstance(req_body, dict):
        return create_error_response("Request body must be a JSON object", 400)

    # Validate required fields
    lookup_types = req_body.get('lookup_types', [])
    if not lookup_types:
        return create_error_response("lookup_types array is required", 400)

    if not isinstance(lookup_types, list):
        return create_error_response("lookup_types must be an array", 400)

    if len(lookup_types) > 10:  # Lower limit for cursor pagination
        return create_error_response("Maximum 10 lookup types allowed for cursor pagination", 400)

    # Parse pagination parameters
    cursor = req_body.get('cursor')
    size = req_body.get('size', 20)
    sort_by = req_body.get('sort_by', 'lookup_code')
    sort_order = req_body.get('sort_order', 'asc')

    # Validate pagination parameters
    if not isinstance(size, int) or size < 1 or size > 100:
        return create_error_response("size must be between 1 and 100", 400)

    if sort_by not in ['lookup_code', 'display_name', 'sort_order', 'created_date', 'modified_date']:
        return create_error_response(
            "sort_by must be one of: lookup_code, display_name, sort_order, created_date, modified_date", 
            400
        )

    if sort_order not in ['asc', 'desc']:
        return create_error_response("sort_order must be 'asc' or 'desc'", 400)

    # Parse filter parameters
    search = req_body.get('search', '').strip() or None
    active_only = req_body.get('active_only', True)
    include_inactive_types = req_body.get('include_inactive_types', False)
    group_by_type = req_body.get('group_by_type', True)

    # Get database connection and service
    db = next(get_db())
    lookup_service = PDCLookupService(db)

    # Validate lookup types exist
    valid_types = []
    not_found = []

    for lookup_type in lookup_types:
        db_lookup_type = lookup_service.get_lookup_type(lookup_type)
        if not db_lookup_type:
            not_found.append(lookup_type)
            continue
        # Skip inactive types unless explicitly requested
        if not include_inactive_types and not db_lookup_type.is_active:
            not_found.append(f"{lookup_type} (inactive)")
            continue
        valid_types.append((lookup_type, db_lookup_type))

    if not valid_types:
        return create_error_response("No valid lookup types found", 404, {"not_found": not_found})

    # Create pagination object
    pagination_params = {
        'page_type': 'cursor',
        'cursor': cursor,
        'size': size,
        'sort_by': sort_by,
        'sort_order': sort_order
    }
    pagination = LookupPaginationQueryParser.parse_pagination_params(pagination_params)

    # Get aggregated results across all valid types
    if group_by_type:
        # Group results by lookup type
        result = {
            "lookup_types": [],
            "pagination_type": "cursor",
            "requested_count": len(lookup_types),
            "found_count": len(valid_types),
            "not_found": not_found,
            "total_items": 0,
            "cursor_info": {},
            "query_params": {
                "lookup_types": [lt for lt, _ in valid_types],
                "size": size,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "search": search,
                "active_only": active_only,
                "group_by_type": group_by_type
            }
        }
        # Track pagination across all types
        has_more = False
        next_cursors = {}
        previous_cursors = {}
        for lookup_type, db_lookup_type in valid_types:
            # Get paginated results for this type
            type_result = lookup_service.get_by_type_paginated(
                lookup_type=lookup_type,
                pagination=pagination,
                search=search,
                include_inactive=not active_only
            )
            # Build type response
            type_response = {
                "lookup_type": lookup_type,
                "display_name": db_lookup_type.display_name,
                "description": db_lookup_type.description,
                "is_active": db_lookup_type.is_active,
                "items": type_result["items"],
                "item_count": len(type_result["items"]),
                "pagination": type_result["pagination"]
            }
            result["lookup_types"].append(type_response)
            result["total_items"] += len(type_result["items"])
            # Track pagination state
            if type_result["pagination"].get("next_cursor"):
                has_more = True
                next_cursors[lookup_type] = type_result["pagination"]["next_cursor"]
            if type_result["pagination"].get("previous_cursor"):
                previous_cursors[lookup_type] = type_result["pagination"]["previous_cursor"]
        # Set overall cursor info
        result["cursor_info"] = {
            "current_cursor": cursor,
            "has_more": has_more,
            "cursor_field": sort_by,
            "next_cursors": next_cursors if next_cursors else None,
            "previous_cursors": previous_cursors if previous_cursors else None
        }
    else:
        # Unified results across all types (flattened)
        all_items = []
        pagination_meta = {}
        for lookup_type, db_lookup_type in valid_types:
            # Get paginated results for this type
            type_result = lookup_service.get_by_type_paginated(
                lookup_type=lookup_type,
                pagination=pagination,
                search=search,
                include_inactive=not active_only
            )
            # Add type info to each item
            for item in type_result["items"]:
                item["lookup_type_info"] = {
                    "display_name": db_lookup_type.display_name,
                    "description": db_lookup_type.description
                }
            all_items.extend(type_result["items"])
            # Use pagination from first type (they should be similar)
            if not pagination_meta:
                pagination_meta = type_result["pagination"]
        # Sort unified results
        reverse_sort = sort_order == 'desc'
        if sort_by == 'lookup_code':
            all_items.sort(key=lambda x: x.get('lookup_code', ''), reverse=reverse_sort)
        elif sort_by == 'display_name':
            all_items.sort(key=lambda x: x.get('display_name', ''), reverse=reverse_sort)
        elif sort_by == 'sort_order':
            all_items.sort(key=lambda x: x.get('sort_order', 0), reverse=reverse_sort)
        elif sort_by in ['created_date', 'modified_date']:
            all_items.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse_sort)
        result = {
            "items": all_items[:size],  # Apply size limit to unified results
            "pagination_type": "cursor",
            "lookup_types_info": [
                {
                    "lookup_type": lt,
                    "display_name": db_lt.display_name,
                    "description": db_lt.description,
                    "is_active": db_lt.is_active
                }
                for lt, db_lt in valid_types
            ],
            "requested_count": len(lookup_types),
            "found_count": len(valid_types),
            "not_found": not_found,
            "total_items": len(all_items),
            "pagination": pagination_meta,
            "cursor_info": {
                "current_cursor": cursor,
                "has_more": len(all_items) > size,
                "cursor_field": sort_by,
                "next_cursor": pagination_meta.get("next_cursor") if len(all_items) > size else None,
                "previous_cursor": pagination_meta.get("previous_cursor")
            },
            "query_params": {
                "lookup_types": [lt for lt, _ in valid_types],
                "size": size,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "search": search,
                "active_only": active_only,
                "group_by_type": group_by_type
            }
        }
    try:
        return create_success_response(result)
    except ValueError as ve:
        return create_error_response("Invalid request parameters", 400, str(ve))
    except Exception as e:
        logging.error(f"Get lookup codes batch cursor paginated failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))

@bp.route(route="lookups/batch/codes/cursor/test", methods=["POST"])
def test_batch_cursor_json(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Log all available information
        logging.info("=== DEBUG BATCH CURSOR JSON TEST ===")
        
        # Log headers
        headers_dict = dict(req.headers)
        logging.info(f"Headers: {headers_dict}")
        
        # Log content type specifically
        content_type = req.headers.get('content-type', 'Not specified')
        logging.info(f"Content-Type: {content_type}")
        
        # Try to get raw body
        try:
            raw_body = req.get_body()
            logging.info(f"Raw body (bytes): {raw_body}")
            decoded_body = raw_body.decode('utf-8')
            logging.info(f"Decoded body: {decoded_body}")
        except Exception as raw_error:
            logging.error(f"Error getting raw body: {str(raw_error)}")
        
        # Try to parse JSON
        try:
            req_body = req.get_json()
            logging.info(f"Parsed JSON: {req_body}")
            return create_success_response({
                "status": "success",
                "parsed_json": req_body,
                "content_type": content_type
            })
        except ValueError as ve:
            logging.error(f"JSON parsing failed: {str(ve)}")
            return create_error_response("JSON parsing failed", 400, str(ve))
        except Exception as e:
            logging.error(f"Unexpected JSON error: {str(e)}")
            return create_error_response("Unexpected JSON error", 400, str(e))
            
    except Exception as e:
        logging.error(f"Test endpoint failed: {str(e)}")
        return create_error_response("Test endpoint failed", 500, str(e))

@bp.route(route="lookups/types/{lookup_type}/codes/cursor", methods=["GET"])
def get_lookup_codes_cursor_paginated(req: func.HttpRequest) -> func.HttpResponse:
    try:
        lookup_type = req.route_params.get('lookup_type')
        
        if not lookup_type:
            return create_error_response("Lookup type is required", 400)
        
        # Parse and validate query parameters
        request_params = dict(req.params)
        
        # Validate size parameter
        size = int(request_params.get('size', 20))
        if size < 1 or size > 100:
            return create_error_response("Size must be between 1 and 100", 400)
        
        # Set cursor-based pagination parameters
        cursor_params = {
            'page': 1,  # Not used in cursor pagination
            'size': str(size),
            'sort_by': request_params.get('sort_by', 'lookup_code'),
            'sort_order': request_params.get('sort_order', 'asc'),
            'use_cursor': 'true',  # Force cursor pagination
            'cursor': request_params.get('cursor')  # Can be None for first page
        }
        
        # Validate sort parameters
        valid_sort_fields = ['lookup_code', 'display_name', 'sort_order', 'created_at', 'modified_at']
        if cursor_params['sort_by'] not in valid_sort_fields:
            return create_error_response(
                f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}", 
                400
            )
        
        if cursor_params['sort_order'] not in ['asc', 'desc']:
            return create_error_response("sort_order must be 'asc' or 'desc'", 400)
        
        # Get database connection
        db = next(get_db())
        lookup_service = PDCLookupService(db)
        
        # Verify lookup type exists
        db_lookup_type = lookup_service.get_lookup_type(lookup_type)
        if not db_lookup_type:
            return create_error_response("Lookup type not found", 404)
        
        # Parse pagination parameters using existing parser
        pagination = LookupPaginationQueryParser.parse_pagination_params(cursor_params)
        
        # Get search and active parameters
        search = request_params.get('search', '').strip() or None
        active_only = request_params.get('active_only', 'true').lower() == 'true'
        include_inactive = not active_only
        
        # Get paginated results using cursor-based pagination
        result = lookup_service.get_by_type_paginated(
            lookup_type=lookup_type,
            pagination=pagination,
            search=search,
            include_inactive=include_inactive
        )
        
        # Enhance response with cursor-specific metadata
        cursor_metadata = {
            "lookup_type": lookup_type,
            "lookup_type_info": {
                "display_name": db_lookup_type.display_name,
                "description": db_lookup_type.description,
                "is_active": db_lookup_type.is_active
            },
            "pagination_type": "cursor",
            "cursor_info": {
                "current_cursor": request_params.get('cursor'),
                "next_cursor": result["pagination"].get("next_cursor"),
                "previous_cursor": result["pagination"].get("previous_cursor"),
                "has_more": result["pagination"].get("next_cursor") is not None,
                "cursor_field": cursor_params['sort_by']
            },
            "query_params": {
                "size": size,
                "sort_by": cursor_params['sort_by'],
                "sort_order": cursor_params['sort_order'],
                "search": search,
                "active_only": active_only
            }
        }
        
        # Merge cursor metadata into result
        result.update(cursor_metadata)
        
        return create_success_response(result)
        
    except ValueError as ve:
        return create_error_response("Invalid query parameters", 400, str(ve))
    except Exception as e:
        logging.error(f"Get lookup codes cursor paginated failed: {str(e)}")
        return create_error_response("Failed to retrieve lookup codes", 500, str(e))

@bp.route(route="lookups/summary", methods=["GET"])
def get_lookup_summary(req: func.HttpRequest) -> func.HttpResponse:
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
