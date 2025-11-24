"""
Unified PDC Classification Service

This module provides a comprehensive service for PDC Classification operations,
including basic CRUD operations, advanced pagination, filtering, and search capabilities.
"""
import logging
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
    SortOrder,
    PaginationType
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
    # MODEL TO DICT CONVERSION
    # ========================================
    
    def to_api_dict(self, classification: PDCClassification) -> Dict[str, Any]:
        """Convert classification model to API dictionary format using model's to_dict()."""
        data = classification.to_dict()
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
        include_template: bool = True,
        include_retention: bool = None
    ):
        """Build the base query with smart conditional joins based on actual data needs."""
        from models.pdc_retention_policy import PDCRetentionPolicy
        
        # Start with base query
        from sqlalchemy.orm import joinedload
        query = self.db.query(PDCClassification)
        # Eagerly load relationships for API serialization
        query = query.options(
            joinedload(PDCClassification.library),
            joinedload(PDCClassification.retention_policy),
            joinedload(PDCClassification.template)
        )
        
        # Smart join logic: only join retention policy when ACTUALLY needed
        needs_retention_join = False
        
        if include_retention is True:
            # Explicitly requested
            needs_retention_join = True
        elif include_retention is None:
            # Auto-detect: only join if we're actually filtering or searching retention fields
            if filters:
                retention_filters = [
                    'retention_policy_id', 'retention_code', 'retention_type', 
                    'jurisdiction', 'trigger_event', 'min_retention_years', 'max_retention_years'
                ]
                needs_retention_join = any(k in retention_filters for k in filters.keys())
            
            # For search: only join if search is specifically for retention data
            # Most searches are for classification name/code, not retention fields
            if search and search.strip() and not needs_retention_join:
                # Only join for retention search if search looks like retention data
                search_lower = search.lower().strip()
                retention_keywords = ['retention', 'legal', 'jurisdiction', 'trigger', 'policy']
                needs_retention_join = any(keyword in search_lower for keyword in retention_keywords)
        
        if needs_retention_join:
            query = query.join(
                PDCRetentionPolicy, PDCClassification.retention_policy_id == PDCRetentionPolicy.retention_policy_id
            )
            logging.debug("Performance: Added retention policy JOIN (needed for filters/search)")
        else:
            logging.debug("Performance: Skipped retention policy JOIN (not needed)")
        
        # Only join template if explicitly needed
        needs_template_join = (
            include_template and (
                (filters and 'template_id' in filters) or
                include_template is True  # Explicitly requested for response data
            )
        )
        
        if needs_template_join:
            query = query.outerjoin(
                PDCTemplate, PDCClassification.template_id == PDCTemplate.template_id
            )
            logging.debug("Performance: Added template JOIN")
        else:
            logging.debug("Performance: Skipped template JOIN")
        
        # Apply deletion filter
        if not include_deleted:
            query = query.filter(PDCClassification.is_deleted == False)
        
        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)
        
        # Apply search with smart retention field inclusion
        if search and search.strip():
            query = self._apply_search(query, search.strip(), include_retention_search=needs_retention_join)
        
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
        
        # Retention Policy filters
        from models.pdc_retention_policy import PDCRetentionPolicy
        
        if 'retention_policy_id' in filters and filters['retention_policy_id']:
            query = query.filter(PDCClassification.retention_policy_id == filters['retention_policy_id'])
            
        if 'retention_code' in filters and filters['retention_code']:
            query = query.filter(PDCRetentionPolicy.retention_code == filters['retention_code'])
            
        if 'retention_type' in filters and filters['retention_type']:
            query = query.filter(PDCRetentionPolicy.retention_type == filters['retention_type'])
            
        if 'jurisdiction' in filters and filters['jurisdiction']:
            query = query.filter(PDCRetentionPolicy.jurisdiction == filters['jurisdiction'])
            
        if 'trigger_event' in filters and filters['trigger_event']:
            query = query.filter(PDCRetentionPolicy.trigger_event == filters['trigger_event'])
        
        # Retention period range filters (convert years to days)
        if 'min_retention_years' in filters and filters['min_retention_years'] is not None:
            min_days = filters['min_retention_years'] * 365
            query = query.filter(PDCRetentionPolicy.retention_period_days >= min_days)
            
        if 'max_retention_years' in filters and filters['max_retention_years'] is not None:
            max_days = filters['max_retention_years'] * 365
            query = query.filter(PDCRetentionPolicy.retention_period_days <= max_days)
        
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
    
    def _apply_search(self, query, search: str, include_retention_search: bool = True):
        """Apply smart full-text search across classification fields and optionally retention fields."""
        from models.pdc_retention_policy import PDCRetentionPolicy
        
        search_term = f"%{search}%"
        
        # Always search core classification fields (these are fast - no JOIN needed)
        classification_search = or_(
            PDCClassification.name.ilike(search_term),
            PDCClassification.description.ilike(search_term),
            PDCClassification.code.ilike(search_term),
            PDCClassification.series.ilike(search_term),
            PDCClassification.classification_purpose.ilike(search_term),
            PDCClassification.citation.ilike(search_term),
            PDCClassification.media_type.ilike(search_term),
            PDCClassification.file_type.ilike(search_term)
        )
        
        # Only include retention policy search if retention JOIN is already happening
        if include_retention_search:
            retention_search = or_(
                PDCRetentionPolicy.retention_code.ilike(search_term),
                PDCRetentionPolicy.retention_type.ilike(search_term),
                PDCRetentionPolicy.jurisdiction.ilike(search_term),
                PDCRetentionPolicy.legal_basis.like(search_term),
                PDCRetentionPolicy.applicable_data_types.like(search_term)
            )
            
            search_filter = or_(classification_search, retention_search)
        else:
            search_filter = classification_search
        
        return query.filter(search_filter)
    
    def _create_minimal_response_dict(self, classification: PDCClassification) -> Dict[str, Any]:
        """Create minimal response dictionary for performance."""
        return {
            'classification_id': classification.classification_id,
            'classification_code': classification.code,
            'name': classification.name,
            'is_active': classification.is_active,
            'classification_level': classification.classification_level,
            'organization_id': classification.organization_id
        }
    
    def _filter_response_fields(self, data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """Filter response to include only requested fields."""
        if not fields:
            return data
        
        filtered = {}
        for field in fields:
            field = field.strip()
            if field in data:
                filtered[field] = data[field]
        
        return filtered
    
    def _needs_retention_data_for_response(self, minimal: bool, fields: Optional[List[str]]) -> bool:
        """Check if retention policy data is needed for the response."""
        if minimal:
            return False  # Minimal responses don't include retention data
            
        if fields:
            # Check if any requested fields are retention-related
            retention_response_fields = [
                'retention_policy_id', 'retention_code', 'retention_type', 
                'jurisdiction', 'legal_basis', 'trigger_event', 'retention_period_days'
            ]
            return any(field.strip() in retention_response_fields for field in fields)
        
        # For full responses, we don't actually need retention JOIN for basic classification data
        # The classification.retention_policy_id is already available without JOIN
        return False
    
    # ========================================
    # BASIC CRUD OPERATIONS
    # ========================================
    
    def create(self, classification_data: PDCClassificationCreate) -> PDCClassification:
        """Create a new PDC Classification."""
        # Map API fields to database model fields
        create_dict = classification_data.dict(exclude_unset=True)
        
        # Map API field names to database field names
        file_type_value = create_dict.get('file_type')
        if file_type_value and len(file_type_value) > 20:
            file_type_value = file_type_value[:20]  # Truncate to 20 chars max
            
        db_data = {
            'code': create_dict.get('classification_code'),
            'name': create_dict.get('name') or create_dict.get('classification_code'),
            'description': create_dict.get('description'),
            'old_classification_id': create_dict.get('old_classification_id'),
            'retention_policy_id': create_dict.get('retention_policy_id'),
            'organization_id': create_dict.get('organization_id', 1),
            'library_id': create_dict.get('library_id'),
            'condition_event': create_dict.get('condition_event'),
            'condition_offset_days': create_dict.get('condition_offset_days'),
            'condition_type': create_dict.get('condition_type'),
            'destruction_method': create_dict.get('destruction_method'),
            'condition': create_dict.get('condition'),
            'vital': create_dict.get('vital'),
            'citation': create_dict.get('citation'),
            'see': create_dict.get('see'),
            'file_type': file_type_value,
            'series': create_dict.get('series'),
            'classification_level': create_dict.get('classification_level'),
            'sensitivity_rating': create_dict.get('sensitivity_rating'),
            'media_type': create_dict.get('media_type'),
            'template_id': create_dict.get('template_id'),
            'classification_purpose': create_dict.get('classification_purpose'),
            'requires_tax_clearance': create_dict.get('requires_tax_clearance'),
            'label_format': create_dict.get('label_format'),
            'secure': create_dict.get('secure'),
            'effective_date': create_dict.get('effective_date'),
            'record_owner_id': create_dict.get('record_owner_id'),
            'record_owner': create_dict.get('record_owner'),
            'record_office': create_dict.get('record_office'),
            'purpose': create_dict.get('purpose'),
            'active_storage': create_dict.get('active_storage'),
            'is_active': create_dict.get('is_active', True),
            'created_by': create_dict.get('created_by', 'api_user'),
        }
        
        # Remove None values
        db_data = {k: v for k, v in db_data.items() if v is not None}
        
        db_classification = PDCClassification(**db_data)
        self.db.add(db_classification)
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def get_by_id(self, classification_id: int, include_deleted: bool = False) -> Optional[PDCClassification]:
        """Get PDC Classification by ID with template information."""
        # Always join retention policy for single-record fetches to ensure relationship is loaded
        query = self._build_base_query(include_deleted=include_deleted, include_template=True, include_retention=True)
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
        
        # Update only provided fields with field mapping
        update_dict = classification_data.dict(exclude_unset=True)
        
        # Direct field mapping (most fields match between API and DB)
        field_mapping = {
            'classification_code': 'code',
            'name': 'name',
            'description': 'description',
            'is_active': 'is_active',
            'classification_level': 'classification_level',
            'media_type': 'media_type',
            'file_type': 'file_type',
            'series': 'series',
            'retention_policy_id': 'retention_policy_id',
            'organization_id': 'organization_id',
        }
        
        # Set modified timestamp
        db_classification.modified_at = datetime.utcnow()
        db_classification.modified_by = 'api_user'  # Default user
        
        for api_field, value in update_dict.items():
            if api_field in field_mapping:
                db_field = field_mapping[api_field]
                if api_field == 'file_type' and value and len(value) > 20:
                    value = value[:20]  # Truncate file_type to 20 chars max
                setattr(db_classification, db_field, value)
        
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
        db_classification.is_active = False  # Mark as inactive when deleted
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
    
    def get_all_paginated_optimized(
        self,
        pagination: PaginationRequest,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_deleted: bool = False,
        minimal: bool = False,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimized version of get_all_paginated with performance enhancements.
        
        Args:
            pagination: Pagination parameters
            filters: Dictionary of filters to apply
            search: Search term for full-text search
            include_deleted: Whether to include deleted records
            minimal: Return minimal response for better performance
            fields: Specific fields to include in response
            
        Returns:
            Paginated response with performance optimizations
        """
        import time
        start_time = time.time()
        
        # Smart join detection - avoid unnecessary joins
        include_template = not minimal and (not fields or any(f.startswith('template') for f in fields))
        
        # Only include retention JOIN if actually needed for filtering, searching, or response
        needs_retention = (
            self._needs_retention_data_for_response(minimal, fields) or
            (filters and any(k in ['retention_policy_id', 'retention_code', 'retention_type', 
                                 'jurisdiction', 'trigger_event', 'min_retention_years', 'max_retention_years'] 
                           for k in filters.keys())) if filters else False
        )
        
        # Build optimized query
        query = self._build_base_query(
            filters=filters, 
            search=search, 
            include_deleted=include_deleted,
            include_template=include_template,
            include_retention=needs_retention
        )
        
        # Always use cursor pagination if explicitly requested
        if getattr(pagination, 'pagination_type', None) == PaginationType.CURSOR or getattr(pagination, 'use_cursor', False):
            result = self._cursor_paginated_response_optimized(query, pagination, minimal, fields)
        else:
            # Use smart pagination strategy
            if pagination.page > 5 or pagination.size > 50:
                pagination.pagination_type = PaginationType.CURSOR
                result = self._cursor_paginated_response_optimized(query, pagination, minimal, fields)
            else:
                count_query = self._build_base_query(
                    filters=filters, 
                    search=search, 
                    include_deleted=include_deleted,
                    include_template=False,  # Don't join template for count
                    include_retention=needs_retention
                )
                result = self._offset_paginated_response_optimized(query, count_query, pagination, filters or {}, search or "", minimal, fields)
        
        # Add performance metrics
        execution_time = (time.time() - start_time) * 1000
        result["performance"] = {
            "query_time_ms": round(execution_time, 2),
            "optimizations_applied": {
                "minimal_response": minimal,
                "field_filtering": bool(fields),
                "smart_joins": True,
                "pagination_strategy": pagination.pagination_type.value
            }
        }
        
        return result

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
    
    def _offset_paginated_response_optimized(
        self, 
        query, 
        count_query, 
        pagination: PaginationRequest,
        filters: Dict[str, Any],
        search: str,
        minimal: bool = False,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Optimized offset-based pagination with minimal responses."""
        # Apply pagination
        items, pagination_response = AdvancedPagination.offset_pagination(
            query=query,
            model_class=PDCClassification,
            pagination=pagination,
            count_query=count_query
        )
        # Ensure items are ORM objects (not dicts)
        orm_items = []
        for item in items:
            if isinstance(item, dict):
                # If item is a dict, try to fetch ORM object by ID
                classification_id = item.get('classification_id') or item.get('id')
                if classification_id:
                    orm_item = self.get_by_id(classification_id)
                    if orm_item:
                        orm_items.append(orm_item)
                    else:
                        orm_items.append(item)
                else:
                    orm_items.append(item)
            else:
                orm_items.append(item)
        # Convert items to API dict format with optimizations
        serialized_items = []
        for item in orm_items:
            if item is None:
                logging.error("Paginated response contains None item. Skipping.")
                continue
            logging.info(f"Paginated item type: {type(item)} | Value: {repr(item)}")
            if minimal:
                api_data = self._create_minimal_response_dict(item)
            else:
                api_data = self.to_api_dict(item)
            if api_data is None:
                logging.error(f"Serialization produced None for item: {repr(item)}. Skipping.")
                continue
            if fields:
                api_data = self._filter_response_fields(api_data, fields)
            serialized_items.append(api_data)
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "filters_applied": filters,
            "sort_info": {
                "sort_by": pagination.sort_by,
                "sort_order": pagination.sort_order.value
            },
            "search_applied": search,
            "response_optimizations": {
                "minimal": minimal,
                "fields_filtered": bool(fields),
                "item_count": len(serialized_items)
            }
        }

    def _cursor_paginated_response_optimized(
        self, 
        query, 
        pagination: PaginationRequest,
        minimal: bool = False,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Optimized cursor-based pagination with minimal responses."""
        # Determine cursor field and value
        # Always use string name for cursor_field
        cursor_field_name = pagination.sort_by if isinstance(pagination.sort_by, str) else 'classification_id'
        cursor_value = None
        if pagination.cursor:
            try:
                cursor_value = int(pagination.cursor)
            except ValueError:
                cursor_value = None
        # Apply cursor pagination
        # Ensure sort_order is always an Enum, not a string, and robust to invalid values
        if isinstance(pagination.sort_order, SortOrder):
            sort_order = pagination.sort_order
        else:
            try:
                sort_order = SortOrder(str(pagination.sort_order).lower())
            except ValueError:
                sort_order = SortOrder.DESC
        items, next_cursor, previous_cursor = AdvancedPagination.cursor_pagination(
            query=query,
            model_class=PDCClassification,
            cursor_field=cursor_field_name,
            cursor_value=cursor_value,
            limit=pagination.size,
            sort_order=sort_order  # Always Enum
        )
        # Ensure items are ORM objects (not dicts)
        orm_items = []
        for item in items:
            if isinstance(item, dict):
                classification_id = item.get('classification_id') or item.get('id')
                if classification_id:
                    orm_item = self.get_by_id(classification_id)
                    if orm_item:
                        orm_items.append(orm_item)
                    else:
                        orm_items.append(item)
                else:
                    orm_items.append(item)
            else:
                orm_items.append(item)
        # Create pagination response
        pagination_response = PaginationResponse.from_cursor_pagination(
            page=pagination.page,
            size=pagination.size,
            total=-1,  # Not calculated for cursor pagination (performance)
            next_cursor=next_cursor,
            previous_cursor=previous_cursor
        )
        # Convert items to API dict format with optimizations
        serialized_items = []
        for item in orm_items:
            if item is None:
                logging.error("Paginated response contains None item. Skipping.")
                continue
            logging.info(f"Paginated item type: {type(item)} | Value: {repr(item)}")
            if minimal:
                api_data = self._create_minimal_response_dict(item)
            else:
                api_data = self.to_api_dict(item)
            if api_data is None:
                logging.error(f"Serialization produced None for item: {repr(item)}. Skipping.")
                continue
            if fields:
                api_data = self._filter_response_fields(api_data, fields)
            serialized_items.append(api_data)
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "sort_info": {
                "sort_by": cursor_field_name,
                "sort_order": pagination.sort_order.value if hasattr(pagination.sort_order, "value") else str(pagination.sort_order),
                "pagination_type": "cursor"
            },
            "response_optimizations": {
                "minimal": minimal,
                "fields_filtered": bool(fields),
                "item_count": len(serialized_items)
            }
        }
    
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
        
        # Convert items to API dict format using model's to_dict method
        serialized_items = []
        for item in items:
            api_data = self.to_api_dict(item)
            serialized_items.append(api_data)
        
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
        
        # Convert items to API dict format using model's to_dict method
        serialized_items = []
        for item in items:
            api_data = self.to_api_dict(item)
            serialized_items.append(api_data)
        
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
        # Determine pagination type based on use_cursor parameter
        use_cursor = request_params.get('use_cursor', 'false').lower() == 'true'
        pagination_type = PaginationType.CURSOR if use_cursor else PaginationType.OFFSET
        
        return PaginationRequest(
            page=int(request_params.get('page', 1)),
            size=int(request_params.get('size', 20)),
            sort_by=request_params.get('sort_by', 'classification_id'),
            sort_order=SortOrder(request_params.get('sort_order', 'asc')),
            pagination_type=pagination_type,
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
