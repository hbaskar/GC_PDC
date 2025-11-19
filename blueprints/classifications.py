"""
Classification API Blueprint
Contains all classification-related endpoints with performance optimizations.
"""
import azure.functions as func
import logging
import math
import time
from typing import Optional
from functools import wraps
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

def monitor_performance(endpoint_name: str):
    """Decorator to monitor endpoint performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                logging.info(f"Performance: {endpoint_name} completed in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logging.error(f"Performance: {endpoint_name} failed after {execution_time:.2f}ms - {str(e)}")
                raise
        return wrapper
    return decorator

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

def create_success_response(data: dict, status_code: int = 200, compress: bool = False) -> func.HttpResponse:
    """Create standardized success response with optional compression."""
    import json
    import gzip
    
    response_body = json.dumps(data, default=str)
    
    # Enable compression for large responses (>1KB) if requested
    if compress and len(response_body) > 1024:
        try:
            compressed_body = gzip.compress(response_body.encode('utf-8'))
            # Only use compression if it actually reduces size significantly
            if len(compressed_body) < len(response_body) * 0.8:
                return func.HttpResponse(
                    compressed_body,
                    status_code=status_code,
                    headers={
                        'Content-Type': 'application/json',
                        'Content-Encoding': 'gzip'
                    }
                )
        except Exception as e:
            logging.warning(f"Compression failed, returning uncompressed: {str(e)}")
    
    return func.HttpResponse(
        response_body,
        status_code=status_code,
        mimetype="application/json"
    )

@bp.route(route="classifications", methods=["GET"])
@monitor_performance("get_all_classifications")
def get_all_classifications(req: func.HttpRequest) -> func.HttpResponse:
    """Get all PDC classifications with advanced pagination and performance optimizations."""
    try:
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Parse query parameters
        request_params = dict(req.params)
        
        # Performance optimization flags
        minimal = request_params.get('minimal', 'false').lower() in ('true', '1', 'yes')
        fields = request_params.get('fields', '').split(',') if request_params.get('fields') else None
        compress_response = request_params.get('compress', 'true').lower() in ('true', '1', 'yes')
        
        # Parse pagination parameters
        pagination = PaginationQueryParser.parse_pagination_params(request_params)
        
        # Parse filter parameters
        filters = PaginationQueryParser.parse_filter_params(request_params)
        
        # Get search parameter
        search = request_params.get('search', '').strip() or None
        include_deleted = request_params.get('include_deleted', 'false').lower() in ('true', '1', 'yes')
        
        # Get paginated results with performance optimizations
        result = service.get_all_paginated_optimized(
            pagination=pagination,
            filters=filters,
            search=search,
            include_deleted=include_deleted,
            minimal=minimal,
            fields=fields
        )
        
        return create_success_response(result, compress=compress_response)
    except Exception as e:
        logging.error(f"Error getting classifications: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@bp.route(route="classifications/summary", methods=["GET"])
@monitor_performance("get_classifications_summary")
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

@bp.route(route="classifications/performance-test", methods=["GET"])
@monitor_performance("classification_performance_test")
def test_classification_performance(req: func.HttpRequest) -> func.HttpResponse:
    """Test endpoint to demonstrate performance improvements with and without retention JOIN."""
    try:
        import time
        
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Parse query parameters
        request_params = dict(req.params)
        test_type = request_params.get('type', 'comparison')  # 'comparison', 'minimal', 'search'
        
        results = {}
        
        if test_type == 'comparison':
            # Test 1: With retention JOIN (old way)
            start_time = time.time()
            query_with_join = service._build_base_query(include_retention=True, include_template=False)
            items_with_join = query_with_join.limit(20).all()
            time_with_join = (time.time() - start_time) * 1000
            
            # Test 2: Without retention JOIN (optimized way)  
            start_time = time.time()
            query_without_join = service._build_base_query(include_retention=False, include_template=False)
            items_without_join = query_without_join.limit(20).all()
            time_without_join = (time.time() - start_time) * 1000
            
            results = {
                "test_type": "JOIN comparison",
                "with_retention_join": {
                    "query_time_ms": round(time_with_join, 2),
                    "items_count": len(items_with_join)
                },
                "without_retention_join": {
                    "query_time_ms": round(time_without_join, 2),
                    "items_count": len(items_without_join)
                },
                "performance_improvement": {
                    "time_saved_ms": round(time_with_join - time_without_join, 2),
                    "percentage_faster": round(((time_with_join - time_without_join) / time_with_join * 100), 1) if time_with_join > 0 else 0
                },
                "explanation": "Shows performance difference between queries with and without retention policy JOIN"
            }
            
        elif test_type == 'search':
            # Test search performance
            search_term = request_params.get('search', 'document')
            
            # Smart search (optimized)
            start_time = time.time()
            query_smart = service._build_base_query(search=search_term, include_retention=None)  # Auto-detect
            items_smart = query_smart.limit(10).all()
            time_smart = (time.time() - start_time) * 1000
            
            # Always JOIN search (old way)
            start_time = time.time()
            query_always_join = service._build_base_query(search=search_term, include_retention=True)
            items_always_join = query_always_join.limit(10).all()
            time_always_join = (time.time() - start_time) * 1000
            
            results = {
                "test_type": "search performance comparison",
                "search_term": search_term,
                "smart_search": {
                    "query_time_ms": round(time_smart, 2),
                    "items_found": len(items_smart),
                    "description": "Only JOINs retention if search term suggests retention data needed"
                },
                "always_join_search": {
                    "query_time_ms": round(time_always_join, 2), 
                    "items_found": len(items_always_join),
                    "description": "Always JOINs retention policy (old behavior)"
                },
                "performance_improvement": {
                    "time_saved_ms": round(time_always_join - time_smart, 2),
                    "percentage_faster": round(((time_always_join - time_smart) / time_always_join * 100), 1) if time_always_join > 0 else 0
                }
            }
        
        else:  # minimal test
            # Test minimal vs full response
            pagination = PaginationQueryParser.parse_pagination_params({'page': '1', 'size': '10'})
            
            start_time = time.time()
            full_result = service.get_all_paginated_optimized(pagination, minimal=False)
            full_time = (time.time() - start_time) * 1000
            
            start_time = time.time()
            minimal_result = service.get_all_paginated_optimized(pagination, minimal=True)
            minimal_time = (time.time() - start_time) * 1000
            
            results = {
                "test_type": "minimal vs full response",
                "full_response": {
                    "query_time_ms": round(full_time, 2),
                    "response_size_chars": len(str(full_result)),
                    "includes_all_fields": True
                },
                "minimal_response": {
                    "query_time_ms": round(minimal_time, 2),
                    "response_size_chars": len(str(minimal_result)),
                    "includes_essential_fields_only": True
                },
                "performance_improvement": {
                    "time_saved_ms": round(full_time - minimal_time, 2),
                    "size_reduction_percentage": round((1 - len(str(minimal_result)) / len(str(full_result))) * 100, 1) if len(str(full_result)) > 0 else 0
                }
            }
        
        return create_success_response(results)
        
    except Exception as e:
        logging.error(f"Performance test failed: {str(e)}")
        return create_error_response("Performance test failed", 500, str(e))

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
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(classification)
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
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(new_classification)
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
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(updated_classification)
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
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(deleted_classification)
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
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(restored_classification)
        return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid classification ID", 400)
    except Exception as e:
        logging.error(f"Restore classification failed: {str(e)}")
        return create_error_response("Failed to restore classification", 500, str(e))
