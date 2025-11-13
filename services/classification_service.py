"""
Unified PDC Classification Service

This module provides a comprehensive service for PDC Classification operations,
including basic CRUD operations, advanced pagination, filtering, and search capabilities.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc

from models import PDCClassification, PDCTemplate
from schemas.classification_schemas import PDCClassificationCreate, PDCClassificationUpdate, PDCClassificationResponse
from services.pagination import (
    AdvancedPagination, 
    PaginationRequest, 
    PaginationResponse, 
    SortOrder
)

class PDCClassificationService:
    """
    Unified PDC Classification service with comprehensive CRUD and pagination capabilities.
    
    This service combines basic CRUD operations with advanced pagination, filtering,
    and search functionality in a single, cohesive interface.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================
    # TEMPLATE ENRICHMENT
    # ========================================
    
    def _enrich_classification_with_template(self, classification: PDCClassification) -> Dict[str, Any]:
        """Enrich classification data with template information."""
        # Convert to dict
        data = classification.__dict__.copy()
        
        # Remove SQLAlchemy internal state
        data.pop('_sa_instance_state', None)
        
        # Add template name if template exists
        if hasattr(classification, 'template') and classification.template:
            data['template_name'] = classification.template.template_name
        else:
            data['template_name'] = None
            
        return data
    
    # ========================================
    # QUERY BUILDING AND FILTERING
    # ========================================
    
    def _build_base_query(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_deleted: bool = False,
        include_template: bool = True
    ):
        """Build the base query with optional joins and filters."""
        if include_template:
            query = self.db.query(PDCClassification).outerjoin(
                PDCTemplate, PDCClassification.template_id == PDCTemplate.template_id
            )
        else:
            query = self.db.query(PDCClassification)
        
        # Apply deletion filter
        if not include_deleted:
            query = query.filter(PDCClassification.is_deleted == False)
        
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
            query = query.filter(PDCClassification.is_active == filters['is_active'])
        
        # String filters
        if 'classification_level' in filters and filters['classification_level']:
            query = query.filter(PDCClassification.classification_level == filters['classification_level'])
        
        if 'media_type' in filters and filters['media_type']:
            query = query.filter(PDCClassification.media_type == filters['media_type'])
        
        if 'file_type' in filters and filters['file_type']:
            query = query.filter(PDCClassification.file_type == filters['file_type'])
        
        if 'series' in filters and filters['series']:
            query = query.filter(PDCClassification.series == filters['series'])
        
        # Numeric filters
        if 'organization_id' in filters and filters['organization_id']:
            query = query.filter(PDCClassification.organization_id == filters['organization_id'])
        
        if 'template_id' in filters and filters['template_id']:
            query = query.filter(PDCClassification.template_id == filters['template_id'])
        
        # Sensitivity rating filters
        if 'sensitivity_min' in filters and filters['sensitivity_min'] is not None:
            query = query.filter(PDCClassification.sensitivity_rating >= filters['sensitivity_min'])
        
        if 'sensitivity_max' in filters and filters['sensitivity_max'] is not None:
            query = query.filter(PDCClassification.sensitivity_rating <= filters['sensitivity_max'])
        
        # Date filters
        if 'created_after' in filters and filters['created_after']:
            query = query.filter(PDCClassification.created_at >= filters['created_after'])
        
        if 'created_before' in filters and filters['created_before']:
            query = query.filter(PDCClassification.created_at <= filters['created_before'])
        
        return query
    
    def _apply_search(self, query, search: str):
        """Apply full-text search across multiple fields."""
        search_term = f"%{search}%"
        
        search_filter = or_(
            PDCClassification.name.ilike(search_term),
            PDCClassification.description.ilike(search_term),
            PDCClassification.code.ilike(search_term),
            PDCClassification.series.ilike(search_term),
            PDCClassification.classification_purpose.ilike(search_term),
            PDCClassification.citation.ilike(search_term),
            PDCClassification.media_type.ilike(search_term),
            PDCClassification.file_type.ilike(search_term)
        )
        
        return query.filter(search_filter)
    
    # ========================================
    # BASIC CRUD OPERATIONS
    # ========================================
    
    def create(self, classification_data: PDCClassificationCreate) -> PDCClassification:
        """Create a new PDC Classification."""
        db_classification = PDCClassification(**classification_data.dict())
        self.db.add(db_classification)
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def get_by_id(self, classification_id: int, include_deleted: bool = False) -> Optional[PDCClassification]:
        """Get PDC Classification by ID with template information."""
        query = self._build_base_query(include_deleted=include_deleted, include_template=True)
        return query.filter(PDCClassification.classification_id == classification_id).first()
    
    def get_by_code(self, code: str, include_deleted: bool = False) -> Optional[PDCClassification]:
        """Get PDC Classification by code."""
        query = self._build_base_query(include_deleted=include_deleted, include_template=True)
        return query.filter(PDCClassification.code == code).first()
    
    def update(self, classification_id: int, classification_data: PDCClassificationUpdate) -> Optional[PDCClassification]:
        """Update a PDC Classification."""
        db_classification = self.get_by_id(classification_id)
        if not db_classification:
            return None
        
        # Update only provided fields
        update_data = classification_data.dict(exclude_unset=True)
        
        # Set modified timestamp
        update_data['modified_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_classification, field, value)
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def delete(self, classification_id: int) -> bool:
        """Hard delete a PDC Classification."""
        db_classification = self.get_by_id(classification_id, include_deleted=True)
        if not db_classification:
            return False
        
        self.db.delete(db_classification)
        self.db.commit()
        return True
    
    def soft_delete(self, classification_id: int, deleted_by: Optional[str] = None) -> Optional[PDCClassification]:
        """Soft delete a PDC Classification by setting is_deleted to True."""
        db_classification = self.get_by_id(classification_id)
        if not db_classification:
            return None
        
        # Set deletion fields
        db_classification.is_deleted = True
        db_classification.deleted_at = datetime.utcnow()
        db_classification.deleted_by = deleted_by
        db_classification.modified_at = datetime.utcnow()
        db_classification.modified_by = deleted_by
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def restore(self, classification_id: int, restored_by: Optional[str] = None) -> Optional[PDCClassification]:
        """Restore a soft-deleted PDC Classification."""
        db_classification = self.get_by_id(classification_id, include_deleted=True)
        if not db_classification or not db_classification.is_deleted:
            return None
        
        # Clear deletion fields
        db_classification.is_deleted = False
        db_classification.deleted_at = None
        db_classification.deleted_by = None
        db_classification.modified_at = datetime.utcnow()
        db_classification.modified_by = restored_by
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    # ========================================
    # ADVANCED PAGINATION AND LISTING
    # ========================================
    
    def get_all_paginated(
        self,
        pagination: PaginationRequest,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Get all classifications with advanced pagination support.
        
        Args:
            pagination: Pagination parameters
            filters: Dictionary of filters to apply
            search: Search term for full-text search
            include_deleted: Whether to include deleted records
            
        Returns:
            Paginated response with items and metadata
        """
        
        # Build base query
        query = self._build_base_query(filters, search, include_deleted)
        
        # Build count query for total records (without joins for performance)
        count_query = self._build_base_query(filters, search, include_deleted, include_template=False)
        
        # Choose pagination strategy
        if pagination.use_cursor and pagination.cursor:
            return self._cursor_paginated_response(query, pagination)
        else:
            return self._offset_paginated_response(query, count_query, pagination, filters or {}, search or "")
    
    def get_all_simple(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        classification_level: Optional[str] = None,
        organization_id: Optional[int] = None,
        sensitivity_rating: Optional[int] = None,
        media_type: Optional[str] = None,
        file_type: Optional[str] = None,
        search: Optional[str] = None,
        include_deleted: bool = False
    ) -> tuple[List[PDCClassification], int]:
        """Get all PDC Classifications with simple filtering and pagination (backward compatibility)."""
        
        # Convert parameters to filter dict
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active
        if classification_level:
            filters['classification_level'] = classification_level
        if organization_id:
            filters['organization_id'] = organization_id
        if sensitivity_rating:
            filters['sensitivity_min'] = sensitivity_rating
            filters['sensitivity_max'] = sensitivity_rating
        if media_type:
            filters['media_type'] = media_type
        if file_type:
            filters['file_type'] = file_type
        
        query = self._build_base_query(filters, search, include_deleted)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        classifications = query.order_by(PDCClassification.name).offset(skip).limit(limit).all()
        
        return classifications, total
    
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
            model_class=PDCClassification,
            pagination=pagination,
            count_query=count_query
        )
        
        # Enrich items with template data and serialize
        serialized_items = []
        for item in items:
            enriched_data = self._enrich_classification_with_template(item)
            serialized_items.append(PDCClassificationResponse.model_validate(enriched_data).model_dump())
        
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
    
    def _cursor_paginated_response(
        self, 
        query, 
        pagination: PaginationRequest
    ) -> Dict[str, Any]:
        """Create cursor-based paginated response."""
        
        # Determine cursor field and value
        cursor_field = getattr(PDCClassification, pagination.sort_by, PDCClassification.classification_id)
        cursor_value = None
        
        if pagination.cursor:
            try:
                cursor_value = int(pagination.cursor)
            except ValueError:
                cursor_value = None
        
        # Apply cursor pagination
        items, next_cursor, previous_cursor = AdvancedPagination.cursor_pagination(
            query=query,
            model_class=PDCClassification,
            cursor_field=cursor_field,
            cursor_value=cursor_value,
            limit=pagination.size,
            sort_order=SortOrder.DESC  # Newest first for cursor pagination
        )
        
        # Create pagination response
        pagination_response = PaginationResponse.from_cursor_pagination(
            page=pagination.page,
            size=pagination.size,
            total=-1,  # Not calculated for cursor pagination (performance)
            next_cursor=next_cursor,
            previous_cursor=previous_cursor
        )
        
        # Enrich items with template data and serialize
        serialized_items = []
        for item in items:
            enriched_data = self._enrich_classification_with_template(item)
            serialized_items.append(PDCClassificationResponse.model_validate(enriched_data).model_dump())
        
        # Create custom response with enriched data
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "sort_info": {
                "sort_by": cursor_field.name if hasattr(cursor_field, 'name') else 'classification_id',
                "sort_order": "desc",
                "pagination_type": "cursor"
            }
        }
    
    # ========================================
    # SUMMARY AND STATISTICS
    # ========================================
    
    def get_summary_statistics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get summary statistics for classifications."""
        
        base_query = self._build_base_query(filters, include_deleted=False, include_template=False)
        
        # Total count
        total_count = base_query.count()
        
        # Active vs inactive
        active_count = base_query.filter(PDCClassification.is_active == True).count()
        inactive_count = total_count - active_count
        
        # By classification level
        level_stats = {}
        level_counts = base_query.with_entities(
            PDCClassification.classification_level,
            func.count(PDCClassification.classification_id).label('count')
        ).group_by(PDCClassification.classification_level).all()
        
        for level, count in level_counts:
            level_stats[level or 'Unspecified'] = count
        
        # By sensitivity rating
        sensitivity_stats = {}
        sensitivity_counts = base_query.with_entities(
            PDCClassification.sensitivity_rating,
            func.count(PDCClassification.classification_id).label('count')
        ).group_by(PDCClassification.sensitivity_rating).all()
        
        for rating, count in sensitivity_counts:
            sensitivity_stats[f"Rating_{rating or 'Unspecified'}"] = count
        
        return {
            "total_classifications": total_count,
            "active_classifications": active_count,
            "inactive_classifications": inactive_count,
            "by_classification_level": level_stats,
            "by_sensitivity_rating": sensitivity_stats,
            "filters_applied": filters or {}
        }
    
    # ========================================
    # UTILITY AND REFERENCE DATA
    # ========================================
    
    def get_classification_levels(self) -> List[str]:
        """Get all unique classification levels."""
        levels = self.db.query(PDCClassification.classification_level).distinct().filter(
            and_(
                PDCClassification.classification_level.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [level[0] for level in levels if level[0]]
    
    def get_media_types(self) -> List[str]:
        """Get all unique media types."""
        media_types = self.db.query(PDCClassification.media_type).distinct().filter(
            and_(
                PDCClassification.media_type.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [media_type[0] for media_type in media_types if media_type[0]]
    
    def get_file_types(self) -> List[str]:
        """Get all unique file types."""
        file_types = self.db.query(PDCClassification.file_type).distinct().filter(
            and_(
                PDCClassification.file_type.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [file_type[0] for file_type in file_types if file_type[0]]
    
    def get_series(self) -> List[str]:
        """Get all unique series."""
        series = self.db.query(PDCClassification.series).distinct().filter(
            and_(
                PDCClassification.series.isnot(None),
                PDCClassification.is_deleted == False
            )
        ).all()
        return [s[0] for s in series if s[0]]
    
    def get_by_organization(self, organization_id: int, is_active: Optional[bool] = None) -> List[PDCClassification]:
        """Get all classifications for a specific organization."""
        filters = {'organization_id': organization_id}
        if is_active is not None:
            filters['is_active'] = is_active
        
        query = self._build_base_query(filters, include_deleted=False)
        return query.order_by(PDCClassification.name).all()
    
    def get_by_sensitivity_rating(self, min_rating: int, max_rating: int = None) -> List[PDCClassification]:
        """Get classifications by sensitivity rating range."""
        filters = {'sensitivity_min': min_rating}
        if max_rating:
            filters['sensitivity_max'] = max_rating
        
        query = self._build_base_query(filters, include_deleted=False)
        return query.order_by(PDCClassification.sensitivity_rating.desc()).all()
    
    def update_last_accessed(self, classification_id: int, accessed_by: str) -> Optional[PDCClassification]:
        """Update last accessed information."""
        db_classification = self.get_by_id(classification_id)
        if not db_classification:
            return None
        
        db_classification.last_accessed_at = datetime.utcnow()
        db_classification.last_accessed_by = accessed_by
        
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification


# ========================================
# QUERY PARAMETER PARSERS
# ========================================

class PaginationQueryParser:
    """Utility class for parsing query parameters into structured formats."""
    
    @staticmethod
    def parse_pagination_params(request_params: Dict[str, str]) -> PaginationRequest:
        """Parse pagination parameters from request."""
        return PaginationRequest(
            page=int(request_params.get('page', 1)),
            size=int(request_params.get('size', 20)),
            sort_by=request_params.get('sort_by', 'classification_id'),
            sort_order=SortOrder(request_params.get('sort_order', 'asc')),
            use_cursor=request_params.get('use_cursor', 'false').lower() == 'true',
            cursor=request_params.get('cursor')
        )
    
    @staticmethod
    def parse_filter_params(request_params: Dict[str, str]) -> Dict[str, Any]:
        """Parse filter parameters from request."""
        filters = {}
        
        # Boolean parameters
        if 'is_active' in request_params:
            filters['is_active'] = request_params['is_active'].lower() in ('true', '1', 'yes')
        
        # String parameters
        for param in ['classification_level', 'media_type', 'file_type', 'series']:
            if param in request_params and request_params[param]:
                filters[param] = request_params[param]
        
        # Numeric parameters
        for param in ['organization_id', 'template_id', 'sensitivity_min', 'sensitivity_max']:
            if param in request_params and request_params[param]:
                try:
                    filters[param] = int(request_params[param])
                except ValueError:
                    pass  # Skip invalid numeric values
        
        # Date parameters
        for param in ['created_after', 'created_before']:
            if param in request_params and request_params[param]:
                try:
                    filters[param] = datetime.fromisoformat(request_params[param])
                except ValueError:
                    pass  # Skip invalid date values
        
        return filters
