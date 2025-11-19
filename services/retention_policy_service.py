"""
Unified PDC Retention Policy Service

This module provides a comprehensive service for PDC Retention Policy operations,
including basic CRUD operations, advanced pagination, filtering, and search capabilities.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc

from models import PDCRetentionPolicy, PDCClassification
from schemas.retention_policy_schemas import (
    PDCRetentionPolicyCreate, 
    PDCRetentionPolicyUpdate, 
    PDCRetentionPolicyResponse
)
from services.pagination import (
    AdvancedPagination, 
    PaginationRequest, 
    PaginationResponse, 
    SortOrder,
    PaginationType
)

class PDCRetentionPolicyService:
    """Service class for PDC Retention Policy operations with advanced features."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _build_base_query(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_deleted: bool = False
    ):
        """Build the base query with optional filters."""
        query = self.db.query(PDCRetentionPolicy)
        
        # Apply active filter (assuming is_active exists)
        if not include_deleted:
            query = query.filter(PDCRetentionPolicy.is_active == True)
        
        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)
        
        # Apply search
        if search and search.strip():
            query = self._apply_search(query, search.strip())
        
        return query
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply various filters to the query."""
        
        # Boolean filters
        if 'is_active' in filters and filters['is_active'] is not None:
            query = query.filter(PDCRetentionPolicy.is_active == filters['is_active'])
        
        if 'audit_required' in filters and filters['audit_required'] is not None:
            query = query.filter(PDCRetentionPolicy.audit_required == filters['audit_required'])
        
        # String filters
        if 'retention_type' in filters and filters['retention_type']:
            query = query.filter(PDCRetentionPolicy.retention_type == filters['retention_type'])
        
        if 'jurisdiction' in filters and filters['jurisdiction']:
            query = query.filter(PDCRetentionPolicy.jurisdiction == filters['jurisdiction'])
        
        if 'policy_owner' in filters and filters['policy_owner']:
            query = query.filter(PDCRetentionPolicy.policy_owner == filters['policy_owner'])
        
        if 'review_frequency' in filters and filters['review_frequency']:
            query = query.filter(PDCRetentionPolicy.review_frequency == filters['review_frequency'])
        
        # Range filters for retention period
        if 'retention_days_min' in filters and filters['retention_days_min'] is not None:
            query = query.filter(PDCRetentionPolicy.retention_period_days >= filters['retention_days_min'])
        
        if 'retention_days_max' in filters and filters['retention_days_max'] is not None:
            query = query.filter(PDCRetentionPolicy.retention_period_days <= filters['retention_days_max'])
        
        # Date filters
        if 'created_after' in filters and filters['created_after']:
            query = query.filter(PDCRetentionPolicy.created_at >= filters['created_after'])
        
        if 'created_before' in filters and filters['created_before']:
            query = query.filter(PDCRetentionPolicy.created_at <= filters['created_before'])
        
        return query
    
    def _apply_search(self, query, search: str):
        """Apply full-text search across multiple fields."""
        search_term = f"%{search}%"
        
        search_filter = or_(
            PDCRetentionPolicy.name.ilike(search_term),
            PDCRetentionPolicy.description.ilike(search_term),
            PDCRetentionPolicy.retention_code.ilike(search_term),
            PDCRetentionPolicy.retention_type.ilike(search_term),
            PDCRetentionPolicy.jurisdiction.ilike(search_term),
            PDCRetentionPolicy.policy_owner.ilike(search_term),
            PDCRetentionPolicy.legal_basis.like(search_term),
            PDCRetentionPolicy.applicable_data_types.like(search_term),
            PDCRetentionPolicy.comments.like(search_term)
        )
        
        return query.filter(search_filter)
    
    # ========================================
    # CRUD Operations
    # ========================================
    
    def create(self, policy_data: PDCRetentionPolicyCreate) -> PDCRetentionPolicy:
        """Create a new PDC Retention Policy."""
        db_data = policy_data.dict()
        db_data['created_at'] = datetime.utcnow()
        
        db_policy = PDCRetentionPolicy(**db_data)
        self.db.add(db_policy)
        self.db.commit()
        self.db.refresh(db_policy)
        return db_policy
    
    def get_by_id(self, policy_id: int, include_deleted: bool = False) -> Optional[PDCRetentionPolicy]:
        """Get PDC Retention Policy by ID."""
        query = self._build_base_query(include_deleted=include_deleted)
        return query.filter(PDCRetentionPolicy.retention_policy_id == policy_id).first()
    
    def get_by_code(self, code: str, include_deleted: bool = False) -> Optional[PDCRetentionPolicy]:
        """Get PDC Retention Policy by retention code."""
        query = self._build_base_query(include_deleted=include_deleted)
        return query.filter(PDCRetentionPolicy.retention_code == code).first()
    
    def update(self, policy_id: int, policy_data: PDCRetentionPolicyUpdate) -> Optional[PDCRetentionPolicy]:
        """Update a PDC Retention Policy."""
        db_policy = self.get_by_id(policy_id)
        if not db_policy:
            return None
        
        # Update only provided fields
        update_data = policy_data.dict(exclude_unset=True)
        
        # Set modified timestamp
        update_data['modified_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_policy, field, value)
        
        self.db.commit()
        self.db.refresh(db_policy)
        return db_policy
    
    def delete(self, policy_id: int) -> bool:
        """Hard delete a PDC Retention Policy."""
        db_policy = self.get_by_id(policy_id, include_deleted=True)
        if not db_policy:
            return False
        
        # Check if policy is in use by classifications
        classifications_count = self.db.query(PDCClassification).filter(
            PDCClassification.retention_policy_id == policy_id
        ).count()
        
        if classifications_count > 0:
            raise ValueError(f"Cannot delete retention policy. It is used by {classifications_count} classifications.")
        
        self.db.delete(db_policy)
        self.db.commit()
        return True
    
    def soft_delete(self, policy_id: int, deleted_by: str = "system") -> Optional[PDCRetentionPolicy]:
        """Soft delete a PDC Retention Policy by setting is_active to False."""
        db_policy = self.get_by_id(policy_id)
        if not db_policy:
            return None
        
        db_policy.is_active = False
        db_policy.modified_at = datetime.utcnow()
        db_policy.modified_by = deleted_by
        
        self.db.commit()
        self.db.refresh(db_policy)
        return db_policy
    
    def restore(self, policy_id: int, restored_by: str = "system") -> Optional[PDCRetentionPolicy]:
        """Restore a soft-deleted PDC Retention Policy."""
        db_policy = self.get_by_id(policy_id, include_deleted=True)
        if not db_policy:
            return None
        
        db_policy.is_active = True
        db_policy.modified_at = datetime.utcnow()
        db_policy.modified_by = restored_by
        
        self.db.commit()
        self.db.refresh(db_policy)
        return db_policy
    
    # ========================================
    # Advanced Query Operations
    # ========================================
    
    def get_all_paginated(
        self,
        pagination: PaginationRequest,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Get all retention policies with advanced pagination support.
        
        Args:
            pagination: Pagination parameters
            filters: Dictionary of filters to apply
            search: Search term for full-text search
            include_deleted: Whether to include inactive policies
            
        Returns:
            Paginated response with items and metadata
        """
        
        # Build base query
        query = self._build_base_query(filters, search, include_deleted)
        
        # Build count query for total records (without joins for performance)
        count_query = self._build_base_query(filters, search, include_deleted)
        
        # Choose pagination strategy
        if pagination.use_cursor and pagination.cursor:
            return self._cursor_paginated_response(query, pagination)
        else:
            return self._offset_paginated_response(query, count_query, pagination, filters or {}, search or "")
    
    def _offset_paginated_response(
        self, 
        query, 
        count_query, 
        pagination: PaginationRequest,
        filters: Dict[str, Any],
        search: str
    ) -> Dict[str, Any]:
        """Create offset-based paginated response."""
        
        # Apply pagination
        items, pagination_response = AdvancedPagination.offset_pagination(
            query=query,
            model_class=PDCRetentionPolicy,
            pagination=pagination,
            count_query=count_query
        )
        
        # Enrich items with classification count and serialize
        serialized_items = []
        for item in items:
            enriched_data = self._enrich_policy_with_stats(item)
            serialized_items.append(PDCRetentionPolicyResponse.model_validate(enriched_data).model_dump())
        
        # Create custom response with enriched data
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "filters_applied": filters or {},
            "sort_info": {
                "sort_by": pagination.sort_by,
                "sort_order": pagination.sort_order.value
            },
            "search_applied": search or ""
        }
    
    def _enrich_policy_with_stats(self, policy: PDCRetentionPolicy) -> Dict[str, Any]:
        """Enrich retention policy data with classification count."""
        # Use the model's to_dict method
        data = policy.to_dict()
        
        # Add count of classifications using this policy
        classifications_count = self.db.query(PDCClassification).filter(
            PDCClassification.retention_policy_id == policy.retention_policy_id
        ).count()
        
        data['classifications_count'] = classifications_count
        
        return data
    
    # ========================================
    # Utility and Statistics Operations
    # ========================================
    
    def get_summary_statistics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get retention policy summary statistics."""
        base_query = self._build_base_query(filters, include_deleted=False)
        
        # Basic counts
        total_policies = base_query.count()
        active_policies = base_query.filter(PDCRetentionPolicy.is_active == True).count()
        inactive_policies = total_policies - active_policies
        
        # Group by retention type
        retention_type_stats = dict(
            self.db.query(
                PDCRetentionPolicy.retention_type,
                func.count(PDCRetentionPolicy.retention_policy_id)
            ).filter(PDCRetentionPolicy.is_active == True)
            .group_by(PDCRetentionPolicy.retention_type).all()
        )
        
        # Group by jurisdiction
        jurisdiction_stats = dict(
            self.db.query(
                PDCRetentionPolicy.jurisdiction,
                func.count(PDCRetentionPolicy.retention_policy_id)
            ).filter(PDCRetentionPolicy.is_active == True)
            .group_by(PDCRetentionPolicy.jurisdiction).all()
        )
        
        # Average retention period
        avg_retention_result = self.db.query(
            func.avg(PDCRetentionPolicy.retention_period_days)
        ).filter(PDCRetentionPolicy.is_active == True).scalar()
        
        avg_retention_days = float(avg_retention_result) if avg_retention_result else None
        
        return {
            "total_policies": total_policies,
            "active_policies": active_policies,
            "inactive_policies": inactive_policies,
            "by_retention_type": retention_type_stats,
            "by_jurisdiction": jurisdiction_stats,
            "avg_retention_days": avg_retention_days
        }
    
    def get_retention_types(self) -> List[str]:
        """Get all unique retention types."""
        result = self.db.query(PDCRetentionPolicy.retention_type).filter(
            PDCRetentionPolicy.retention_type.isnot(None),
            PDCRetentionPolicy.is_active == True
        ).distinct().all()
        
        return [r[0] for r in result if r[0]]
    
    def get_jurisdictions(self) -> List[str]:
        """Get all unique jurisdictions."""
        result = self.db.query(PDCRetentionPolicy.jurisdiction).filter(
            PDCRetentionPolicy.jurisdiction.isnot(None),
            PDCRetentionPolicy.is_active == True
        ).distinct().all()
        
        return [r[0] for r in result if r[0]]
    
    def get_policies_by_type(self, retention_type: str) -> List[PDCRetentionPolicy]:
        """Get all policies of a specific retention type."""
        return self.db.query(PDCRetentionPolicy).filter(
            PDCRetentionPolicy.retention_type == retention_type,
            PDCRetentionPolicy.is_active == True
        ).all()
    
    # ========================================
    # Static Utility Methods
    # ========================================
    
    @staticmethod
    def parse_pagination_params(request_params: Dict[str, str]) -> PaginationRequest:
        """Parse pagination parameters from request."""
        # Determine pagination type based on use_cursor parameter
        use_cursor = request_params.get('use_cursor', 'false').lower() == 'true'
        pagination_type = PaginationType.CURSOR if use_cursor else PaginationType.OFFSET
        
        return PaginationRequest(
            page=int(request_params.get('page', 1)),
            size=int(request_params.get('size', 20)),
            sort_by=request_params.get('sort_by', 'retention_policy_id'),
            sort_order=SortOrder(request_params.get('sort_order', 'asc')),
            pagination_type=pagination_type,
            cursor=request_params.get('cursor')
        )
    
    @staticmethod
    def parse_filter_params(request_params: Dict[str, str]) -> Dict[str, Any]:
        """Parse filter parameters from request."""
        filters = {}
        
        # Boolean filters
        if 'is_active' in request_params:
            filters['is_active'] = request_params['is_active'].lower() == 'true'
        
        if 'audit_required' in request_params:
            filters['audit_required'] = request_params['audit_required'].lower() == 'true'
        
        # String filters
        for field in ['retention_type', 'jurisdiction', 'policy_owner', 'review_frequency']:
            if field in request_params and request_params[field]:
                filters[field] = request_params[field]
        
        # Numeric filters
        if 'retention_days_min' in request_params:
            try:
                filters['retention_days_min'] = int(request_params['retention_days_min'])
            except ValueError:
                pass
        
        if 'retention_days_max' in request_params:
            try:
                filters['retention_days_max'] = int(request_params['retention_days_max'])
            except ValueError:
                pass
        
        return filters