"""
Classification API Blueprint
Contains all classification-related endpoints.
"""
import azure.functions as func
import logging
import math
from typing import Optional
from pydantic import ValidationError

# Import dependencies
from database.config import get_db
from models import PDCClassification
from services.classification_service import PDCClassificationService, PaginationQueryParser
from schemas.classification_schemas import (
    PDCClassificationCreate, 
    PDCClassificationUpdate, 
    PDCClassificationResponse,
    PDCClassificationSummary,
    ErrorResponse
)
import json

# Create blueprint
bp = func.Blueprint()

def create_error_response(message: str, status_code: int, detail: str = None) -> func.HttpResponse:
    """Create standardized error response."""
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
    """Create standardized success response."""
    import json
    return func.HttpResponse(
        json.dumps(data, default=str),
        status_code=status_code,
        mimetype="application/json"
    )

@bp.route(route="classifications", methods=["GET"])
def get_all_classifications(req: func.HttpRequest) -> func.HttpResponse:
    """Get all PDC classifications with advanced pagination."""
    try:
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Parse query parameters
        request_params = dict(req.params)
        
        # Parse pagination parameters
        pagination = PaginationQueryParser.parse_pagination_params(request_params)
        
        # Parse filter parameters
        filters = PaginationQueryParser.parse_filter_params(request_params)
        
        # Get search parameter
        search = request_params.get('search', '').strip() or None
        include_deleted = request_params.get('include_deleted', 'false').lower() in ('true', '1', 'yes')
        
        # Get paginated results
        result = service.get_all_paginated(
            pagination=pagination,
            filters=filters,
            search=search,
            include_deleted=include_deleted
        )
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error getting classifications: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@bp.route(route="classifications/summary", methods=["GET"])
def get_classifications_summary(req: func.HttpRequest) -> func.HttpResponse:
    """Get summary statistics for PDC classifications."""
    try:
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Parse query parameters for filtering
        request_params = dict(req.params)
        filters = PaginationQueryParser.parse_filter_params(request_params)
        
        # Get summary
        summary = service.get_summary_statistics(filters)
        
        return func.HttpResponse(
            json.dumps(summary, default=str),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error getting classifications summary: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
def get_classifications(req: func.HttpRequest) -> func.HttpResponse:
    """Get all classifications with optional filtering and pagination."""
    try:
        # Parse query parameters
        page = int(req.params.get('page', 1))
        size = int(req.params.get('size', 10))
        search = req.params.get('search', '')
        active_only = req.params.get('active_only', 'true').lower() == 'true'
        
        # Validate pagination parameters
        if page < 1 or size < 1 or size > 100:
            return create_error_response("Invalid pagination parameters", 400)
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Get classifications with filtering
        classifications, total = service.get_all(
            skip=(page - 1) * size,
            limit=size,
            search=search,
            is_active=active_only
        )
        
        # Convert to response format
        items = [
            PDCClassificationResponse.model_validate(classification).model_dump()
            for classification in classifications
        ]
        
        # Calculate pagination metadata
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
        logging.error(f"Get classifications failed: {str(e)}")
        return create_error_response("Failed to retrieve classifications", 500, str(e))

@bp.route(route="classifications/{classification_id:int}", methods=["GET"])
def get_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific classification by ID."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Get classification
        classification = service.get_by_id(classification_id)
        if not classification:
            return create_error_response("Classification not found", 404)
        
        # Enrich with template data and serialize
        enriched_data = service._enrich_classification_with_template(classification)
        response_data = PDCClassificationResponse.model_validate(enriched_data).model_dump()
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Get classification failed: {str(e)}")
        return create_error_response("Failed to retrieve classification", 500, str(e))

@bp.route(route="classifications", methods=["POST"])
def create_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new classification."""
    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_error_response("Invalid JSON in request body", 400)
        
        if not req_body:
            return create_error_response("Request body is required", 400)
        
        # Validate data using Pydantic schema
        try:
            classification_data = PDCClassificationCreate(**req_body)
        except ValidationError as e:
            return create_error_response("Validation error", 400, str(e))
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Create classification
        new_classification = service.create(classification_data)
        
        response_data = PDCClassificationResponse.model_validate(new_classification).model_dump()
        return create_success_response(response_data, 201)
        
    except Exception as e:
        logging.error(f"Create classification failed: {str(e)}")
        return create_error_response("Failed to create classification", 500, str(e))

@bp.route(route="classifications/{classification_id:int}", methods=["PUT"])
def update_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Update an existing classification."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_error_response("Invalid JSON in request body", 400)
        
        if not req_body:
            return create_error_response("Request body is required", 400)
        
        # Validate data using Pydantic schema
        try:
            classification_data = PDCClassificationUpdate(**req_body)
        except ValidationError as e:
            return create_error_response("Validation error", 400, str(e))
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Update classification
        updated_classification = service.update(classification_id, classification_data)
        if not updated_classification:
            return create_error_response("Classification not found", 404)
        
        response_data = PDCClassificationResponse.model_validate(updated_classification).model_dump()
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Update classification failed: {str(e)}")
        return create_error_response("Failed to update classification", 500, str(e))

@bp.route(route="classifications/{classification_id:int}", methods=["DELETE"])
def delete_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Soft delete a classification (mark as deleted)."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Get optional delete reason from query params
        deleted_by = req.params.get('deleted_by', 'system')
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Soft delete classification
        deleted_classification = service.soft_delete(classification_id, deleted_by)
        if not deleted_classification:
            return create_error_response("Classification not found or already deleted", 404)
        
        # Return the deleted classification
        response_data = PDCClassificationResponse.model_validate(deleted_classification).model_dump()
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Delete classification failed: {str(e)}")
        return create_error_response("Failed to delete classification", 500, str(e))

@bp.route(route="classifications/{classification_id:int}/restore", methods=["POST"])
def restore_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Restore a soft-deleted classification."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Get optional restore reason from request body or query params
        restored_by = req.params.get('restored_by', 'system')
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Restore classification
        restored_classification = service.restore(classification_id, restored_by)
        if not restored_classification:
            return create_error_response("Classification not found or not deleted", 404)
        
        response_data = PDCClassificationResponse.model_validate(restored_classification).model_dump()
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Restore classification failed: {str(e)}")
        return create_error_response("Failed to restore classification", 500, str(e))
