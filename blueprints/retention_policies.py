"""
Azure Functions Blueprint for PDC Retention Policy CRUD operations.
Provides comprehensive API endpoints for managing retention policies.
"""
import azure.functions as func
import json
import logging
from typing import Dict, Any

from database.config import get_db
from services.retention_policy_service import PDCRetentionPolicyService
from schemas.retention_policy_schemas import (
    PDCRetentionPolicyCreate, 
    PDCRetentionPolicyUpdate, 
    PDCRetentionPolicyResponse
)
from pydantic import ValidationError

# Create blueprint
bp = func.Blueprint()

def create_success_response(data: Any, status_code: int = 200) -> func.HttpResponse:
    """Create a successful JSON response."""
    return func.HttpResponse(
        json.dumps(data, default=str),
        status_code=status_code,
        headers={"Content-Type": "application/json"}
    )

def create_error_response(message: str, status_code: int = 400, details: str = None) -> func.HttpResponse:
    """Create an error JSON response."""
    error_data = {"error": message}
    if details:
        error_data["details"] = details
    
    return func.HttpResponse(
        json.dumps(error_data),
        status_code=status_code,
        headers={"Content-Type": "application/json"}
    )

@bp.route(route="retention-policies", methods=["GET"])
def get_retention_policies(req: func.HttpRequest) -> func.HttpResponse:
    """Get all retention policies with pagination, filtering, and search."""
    try:
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Parse query parameters
            request_params = dict(req.params)
            
            # Parse pagination parameters
            pagination = service.parse_pagination_params(request_params)
            
            # Parse filter parameters
            filters = service.parse_filter_params(request_params)
            
            # Get search parameter
            search = request_params.get('search', '').strip()
            include_deleted = request_params.get('include_inactive', 'false').lower() == 'true'
            
            # Get paginated results
            result = service.get_all_paginated(
                pagination=pagination,
                filters=filters if filters else None,
                search=search if search else None,
                include_deleted=include_deleted
            )
            
            return create_success_response(result)
        
    except Exception as e:
        logging.error(f"Get retention policies failed: {str(e)}")
        return create_error_response("Failed to retrieve retention policies", 500, str(e))

@bp.route(route="retention-policies/{policy_id:int}", methods=["GET"])
def get_retention_policy(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific retention policy by ID."""
    try:
        policy_id = int(req.route_params.get('policy_id'))
        
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Get the retention policy
            policy = service.get_by_id(policy_id)
            if not policy:
                return create_error_response("Retention policy not found", 404)
            
            # Enrich with statistics and serialize
            enriched_data = service._enrich_policy_with_stats(policy)
            response_data = PDCRetentionPolicyResponse.model_validate(enriched_data).model_dump()
            return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid retention policy ID", 400)
    except Exception as e:
        logging.error(f"Get retention policy failed: {str(e)}")
        return create_error_response("Failed to retrieve retention policy", 500, str(e))

@bp.route(route="retention-policies", methods=["POST"])
def create_retention_policy(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new retention policy."""
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
            policy_data = PDCRetentionPolicyCreate(**req_body)
        except ValidationError as e:
            return create_error_response("Validation error", 400, str(e))
        
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Check if retention code already exists (if provided)
            if policy_data.retention_code:
                existing = service.get_by_code(policy_data.retention_code)
                if existing:
                    return create_error_response("Retention policy with this code already exists", 409)
            
            # Create the retention policy
            new_policy = service.create(policy_data)
            
            # Enrich and serialize response
            enriched_data = service._enrich_policy_with_stats(new_policy)
            response_data = PDCRetentionPolicyResponse.model_validate(enriched_data).model_dump()
            
            return create_success_response(response_data, 201)
        
    except Exception as e:
        logging.error(f"Create retention policy failed: {str(e)}")
        return create_error_response("Failed to create retention policy", 500, str(e))

@bp.route(route="retention-policies/{policy_id:int}", methods=["PUT"])
def update_retention_policy(req: func.HttpRequest) -> func.HttpResponse:
    """Update an existing retention policy."""
    try:
        policy_id = int(req.route_params.get('policy_id'))
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return create_error_response("Invalid JSON in request body", 400)
        
        if not req_body:
            return create_error_response("Request body is required", 400)
        
        # Validate request data
        try:
            policy_data = PDCRetentionPolicyUpdate(**req_body)
        except ValidationError as e:
            return create_error_response("Validation error", 400, str(e))
        
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Check if retention code already exists (if being updated)
            if policy_data.retention_code:
                existing = service.get_by_code(policy_data.retention_code)
                if existing and existing.retention_policy_id != policy_id:
                    return create_error_response("Retention policy with this code already exists", 409)
            
            # Update the retention policy
            updated_policy = service.update(policy_id, policy_data)
            if not updated_policy:
                return create_error_response("Retention policy not found", 404)
            
            # Enrich and serialize response
            enriched_data = service._enrich_policy_with_stats(updated_policy)
            response_data = PDCRetentionPolicyResponse.model_validate(enriched_data).model_dump()
            return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid retention policy ID", 400)
    except Exception as e:
        logging.error(f"Update retention policy failed: {str(e)}")
        return create_error_response("Failed to update retention policy", 500, str(e))

@bp.route(route="retention-policies/{policy_id:int}", methods=["DELETE"])
def delete_retention_policy(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a retention policy (soft delete by default, hard delete with force=true)."""
    try:
        policy_id = int(req.route_params.get('policy_id'))
        force_delete = req.params.get('force', 'false').lower() == 'true'
        
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            if force_delete:
                # Hard delete
                try:
                    success = service.delete(policy_id)
                    if not success:
                        return create_error_response("Retention policy not found", 404)
                    
                    return create_success_response({"message": "Retention policy permanently deleted"})
                except ValueError as e:
                    return create_error_response(str(e), 409)
            else:
                # Soft delete
                deleted_policy = service.soft_delete(policy_id, "api_user")
                if not deleted_policy:
                    return create_error_response("Retention policy not found", 404)
                
                enriched_data = service._enrich_policy_with_stats(deleted_policy)
                response_data = PDCRetentionPolicyResponse.model_validate(enriched_data).model_dump()
                return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid retention policy ID", 400)
    except Exception as e:
        logging.error(f"Delete retention policy failed: {str(e)}")
        return create_error_response("Failed to delete retention policy", 500, str(e))

@bp.route(route="retention-policies/{policy_id:int}/restore", methods=["POST"])
def restore_retention_policy(req: func.HttpRequest) -> func.HttpResponse:
    """Restore a soft-deleted retention policy."""
    try:
        policy_id = int(req.route_params.get('policy_id'))
        
        # Parse request body for restored_by
        restored_by = "api_user"
        try:
            req_body = req.get_json()
            if req_body and 'restored_by' in req_body:
                restored_by = req_body['restored_by']
        except ValueError:
            pass  # Use default if JSON parsing fails
        
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Restore the retention policy
            restored_policy = service.restore(policy_id, restored_by)
            if not restored_policy:
                return create_error_response("Retention policy not found", 404)
            
            enriched_data = service._enrich_policy_with_stats(restored_policy)
            response_data = PDCRetentionPolicyResponse.model_validate(enriched_data).model_dump()
            return create_success_response(response_data)
        
    except ValueError:
        return create_error_response("Invalid retention policy ID", 400)
    except Exception as e:
        logging.error(f"Restore retention policy failed: {str(e)}")
        return create_error_response("Failed to restore retention policy", 500, str(e))

@bp.route(route="retention-policies/summary", methods=["GET"])
def get_retention_policies_summary(req: func.HttpRequest) -> func.HttpResponse:
    """Get retention policy summary statistics."""
    try:
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Parse filter parameters for summary
            request_params = dict(req.params)
            filters = service.parse_filter_params(request_params)
            
            # Get summary statistics
            summary = service.get_summary_statistics(filters if filters else None)
            
            return create_success_response(summary)
        
    except Exception as e:
        logging.error(f"Get retention policies summary failed: {str(e)}")
        return create_error_response("Failed to retrieve summary statistics", 500, str(e))

@bp.route(route="retention-policies/types", methods=["GET"])
def get_retention_types(req: func.HttpRequest) -> func.HttpResponse:
    """Get all unique retention types."""
    try:
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Get retention types
            types = service.get_retention_types()
            
            return create_success_response({"retention_types": types})
        
    except Exception as e:
        logging.error(f"Get retention types failed: {str(e)}")
        return create_error_response("Failed to retrieve retention types", 500, str(e))

@bp.route(route="retention-policies/jurisdictions", methods=["GET"])
def get_jurisdictions(req: func.HttpRequest) -> func.HttpResponse:
    """Get all unique jurisdictions."""
    try:
        # Get database session
        with get_db() as db:
            service = PDCRetentionPolicyService(db)
            
            # Get jurisdictions
            jurisdictions = service.get_jurisdictions()
            
            return create_success_response({"jurisdictions": jurisdictions})
        
    except Exception as e:
        logging.error(f"Get jurisdictions failed: {str(e)}")
        return create_error_response("Failed to retrieve jurisdictions", 500, str(e))