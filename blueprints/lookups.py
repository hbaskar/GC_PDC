"""
Lookup API Blueprint
Contains all lookup-related endpoints for reference data.
"""
import azure.functions as func
import logging
import math
from typing import Optional
from pydantic import ValidationError

# Import dependencies
from database.config import get_db
from models import PDCLookupType, PDCLookupCode
from services.lookup_service import PDCLookupService
from schemas.lookup_schemas import (
    PDCLookupTypeResponse,
    PDCLookupTypeWithCodes,
    PDCLookupTypeSummary,
    PDCLookupCodeResponse,
    PDCLookupCodeSummary
)
from schemas.pdc_schemas import ErrorResponse

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

@bp.route(route="lookups/types", methods=["GET"])
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

@bp.route(route="lookups/types/{lookup_type}", methods=["GET"])  
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

@bp.route(route="lookups/codes/{lookup_type}", methods=["GET"])
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

@bp.route(route="lookups/batch/codes", methods=["POST"])
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

@bp.route(route="lookups/summary", methods=["GET"])
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