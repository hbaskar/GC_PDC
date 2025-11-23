import azure.functions as func
import logging
import math
import time
from typing import Optional
from functools import wraps
from pydantic import ValidationError
import json

# Create blueprint
bp = func.Blueprint()

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

@bp.route(route="classifications", methods=["GET"])
def get_classifications(req: func.HttpRequest) -> func.HttpResponse:
    """Get all classifications with pagination, filtering, and enrichment."""
    try:
        db = next(get_db())
        service = PDCClassificationService(db)

        # Parse pagination, filter, and search params
        request_params = dict(req.params)
        pagination = PaginationQueryParser.parse_pagination_params(request_params)
        filters = PaginationQueryParser.parse_filter_params(request_params)
        search = request_params.get("search")
        minimal = request_params.get("minimal", "false").lower() == "true"
        fields = request_params.get("fields")
        if fields:
            fields = [f.strip() for f in fields.split(",") if f.strip()]

        # Use optimized paginated service (supports cursor and offset)
        result = service.get_all_paginated_optimized(
            pagination=pagination,
            filters=filters,
            search=search,
            minimal=minimal,
            fields=fields
        )
        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error getting classifications: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get classifications", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


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
        
        return func.HttpResponse(
            json.dumps(results, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Performance test failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Performance test failed", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@bp.route(route="classifications/{classification_id:int}", methods=["GET"])
def get_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific classification by ID."""
    try:
        logging.info(f"Route params: {req.route_params}")
        classification_id = int(req.route_params.get('classification_id'))
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Get classification
        logging.info(f"Fetching classification_id: {classification_id}")
        classification = service.get_by_id(classification_id)
        logging.info(f"Fetched classification: {classification}")
        if not classification:
            return func.HttpResponse(
                json.dumps({"error": "Classification not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Convert to API dict format using schema enrichment (includes retention fields)
        try:
            response_data = PDCClassificationResponse.from_orm_with_retention(classification).model_dump()
            logging.info(f"Response data: {response_data}")
            return func.HttpResponse(
                json.dumps(response_data, default=str),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Error during schema enrichment: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to serialize classification response", "detail": str(e)}),
                status_code=500,
                mimetype="application/json"
            )
        
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid classification ID"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Get classification failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve classification", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@bp.route(route="classifications", methods=["POST"])
def create_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new classification."""
    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate data using Pydantic schema
        try:
            classification_data = PDCClassificationCreate(**req_body)
        except ValidationError as e:
            return func.HttpResponse(
                json.dumps({"error": "Validation error", "detail": str(e)}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Create classification
        new_classification = service.create(classification_data)
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(new_classification)
        return func.HttpResponse(
            json.dumps(response_data, default=str),
            status_code=201,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Create classification failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to create classification", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@bp.route(route="classifications/{classification_id:int}", methods=["PUT"])
def update_classification(req: func.HttpRequest) -> func.HttpResponse:
    """Update an existing classification."""
    try:
        classification_id = int(req.route_params.get('classification_id'))
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate data using Pydantic schema
        try:
            classification_data = PDCClassificationUpdate(**req_body)
        except ValidationError as e:
            return func.HttpResponse(
                json.dumps({"error": "Validation error", "detail": str(e)}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get database connection and service
        db = next(get_db())
        service = PDCClassificationService(db)
        
        # Update classification
        updated_classification = service.update(classification_id, classification_data)
        if not updated_classification:
            return func.HttpResponse(
                json.dumps({"error": "Classification not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(updated_classification)
        return func.HttpResponse(
            json.dumps(response_data, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid classification ID"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Update classification failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to update classification", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

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
            return func.HttpResponse(
                json.dumps({"error": "Classification not found or already deleted"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(deleted_classification)
        return func.HttpResponse(
            json.dumps(response_data, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid classification ID"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Delete classification failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to delete classification", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

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
            return func.HttpResponse(
                json.dumps({"error": "Classification not found or not deleted"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Convert to API dict format using model's to_dict method
        response_data = service.to_api_dict(restored_classification)
        return func.HttpResponse(
            json.dumps(response_data, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid classification ID"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Restore classification failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to restore classification", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
