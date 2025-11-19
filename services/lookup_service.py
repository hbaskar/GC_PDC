"""
Unified PDC Lookup Service

This module provides a comprehensive service for PDC Lookup operations,
including basic CRUD operations, advanced pagination, filtering, and search capabilities.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc

from models import PDCLookupType, PDCLookupCode
from schemas.lookup_schemas import (
    PDCLookupTypeCreate, 
    PDCLookupTypeUpdate,
    PDCLookupCodeCreate,
    PDCLookupCodeUpdate
)
from services.pagination import (
    AdvancedPagination, 
    PaginationRequest, 
    PaginationResponse, 
    SortOrder,
    PaginationType
)

class PDCLookupService:
    """
    Unified PDC Lookup service with comprehensive CRUD and pagination capabilities.
    
    This service combines basic CRUD operations with advanced pagination, filtering,
    and search functionality in a single, cohesive interface for both lookup types and codes.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def to_api_dict_type(self, lookup_type: PDCLookupType) -> Dict[str, Any]:
        """Convert lookup type model to API response dictionary."""
        return lookup_type.to_dict()
    
    def to_api_dict_code(self, lookup_code: PDCLookupCode) -> Dict[str, Any]:
        """Convert lookup code model to API response dictionary."""
        return lookup_code.to_dict()

    # ========================================
    # QUERY BUILDING AND FILTERING
    # ========================================
    
    def _build_base_query_types(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_inactive: bool = False
    ):
        """Build the base query for lookup types with optional filters."""
        query = self.db.query(PDCLookupType)
        
        # Apply active filter
        if not include_inactive:
            query = query.filter(PDCLookupType.is_active == True)
        
        # Apply filters
        if filters:
            query = self._apply_type_filters(query, filters)
        
        # Apply search
        if search and search.strip():
            query = self._apply_type_search(query, search.strip())
        
        return query
    
    def _build_base_query_codes(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_inactive: bool = False
    ):
        """Build the base query for lookup codes with optional filters."""
        query = self.db.query(PDCLookupCode)
        
        # Apply active filter
        if not include_inactive:
            query = query.filter(PDCLookupCode.is_active == True)
        
        # Apply filters
        if filters:
            query = self._apply_code_filters(query, filters)
        
        # Apply search
        if search and search.strip():
            query = self._apply_code_search(query, search.strip())
        
        return query
    
    def _apply_type_filters(self, query, filters: Dict[str, Any]):
        """Apply various filters to lookup type queries."""
        
        # Boolean filters
        if 'is_active' in filters and filters['is_active'] is not None:
            query = query.filter(PDCLookupType.is_active == filters['is_active'])
        
        # String filters
        if 'lookup_type' in filters and filters['lookup_type']:
            query = query.filter(PDCLookupType.lookup_type == filters['lookup_type'])
        
        # Date filters
        if 'created_after' in filters and filters['created_after']:
            query = query.filter(PDCLookupType.created_at >= filters['created_after'])
        
        if 'created_before' in filters and filters['created_before']:
            query = query.filter(PDCLookupType.created_at <= filters['created_before'])
        
        return query
    
    def _apply_code_filters(self, query, filters: Dict[str, Any]):
        """Apply various filters to lookup code queries."""
        
        # Boolean filters
        if 'is_active' in filters and filters['is_active'] is not None:
            query = query.filter(PDCLookupCode.is_active == filters['is_active'])
        
        # String filters
        if 'lookup_type' in filters and filters['lookup_type']:
            query = query.filter(PDCLookupCode.lookup_type == filters['lookup_type'])
        
        if 'lookup_code' in filters and filters['lookup_code']:
            query = query.filter(PDCLookupCode.lookup_code == filters['lookup_code'])
        
        # Numeric filters
        if 'sort_order_min' in filters and filters['sort_order_min'] is not None:
            query = query.filter(PDCLookupCode.sort_order >= filters['sort_order_min'])
        
        if 'sort_order_max' in filters and filters['sort_order_max'] is not None:
            query = query.filter(PDCLookupCode.sort_order <= filters['sort_order_max'])
        
        # Date filters
        if 'created_after' in filters and filters['created_after']:
            query = query.filter(PDCLookupCode.created_at >= filters['created_after'])
        
        if 'created_before' in filters and filters['created_before']:
            query = query.filter(PDCLookupCode.created_at <= filters['created_before'])
        
        return query
    
    def _apply_type_search(self, query, search: str):
        """Apply full-text search to lookup types."""
        search_term = f"%{search}%"
        
        search_filter = or_(
            PDCLookupType.lookup_type.ilike(search_term),
            PDCLookupType.display_name.ilike(search_term),
            PDCLookupType.description.ilike(search_term)
        )
        
        return query.filter(search_filter)
    
    def _apply_code_search(self, query, search: str):
        """Apply full-text search to lookup codes."""
        search_term = f"%{search}%"
        
        search_filter = or_(
            PDCLookupCode.lookup_type.ilike(search_term),
            PDCLookupCode.lookup_code.ilike(search_term),
            PDCLookupCode.display_name.ilike(search_term),
            PDCLookupCode.description.ilike(search_term)
        )
        
        return query.filter(search_filter)

    # ========================================
    # LOOKUP TYPES CRUD OPERATIONS
    # ========================================
    
    def create_lookup_type(self, lookup_type_data: PDCLookupTypeCreate) -> PDCLookupType:
        """Create a new lookup type."""
        db_lookup_type = PDCLookupType(
            lookup_type=lookup_type_data.lookup_type,
            display_name=lookup_type_data.display_name,
            description=lookup_type_data.description,
            created_by=lookup_type_data.created_by,
            created_at=datetime.now(),
            is_active=lookup_type_data.is_active
        )
        self.db.add(db_lookup_type)
        self.db.commit()
        self.db.refresh(db_lookup_type)
        return db_lookup_type
    
    def get_lookup_type(self, lookup_type: str) -> Optional[PDCLookupType]:
        """Get lookup type by ID."""
        return self.db.query(PDCLookupType).filter(
            PDCLookupType.lookup_type == lookup_type
        ).first()
    
    def get_all_lookup_types(self, active_only: bool = True, skip: int = 0, limit: int = None) -> List[PDCLookupType]:
        """Get all lookup types with simple pagination."""
        query = self.db.query(PDCLookupType)
        if active_only:
            query = query.filter(PDCLookupType.is_active == True)
        query = query.order_by(PDCLookupType.lookup_type)
        
        if skip > 0:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
            
        return query.all()
    
    def get_lookup_types_paginated(
        self,
        pagination: PaginationRequest,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Get lookup types with advanced pagination support."""
        
        # Build base query
        query = self._build_base_query_types(filters, search, include_inactive)
        
        # Build count query for total records
        count_query = self._build_base_query_types(filters, search, include_inactive)
        
        # Choose pagination strategy
        if pagination.use_cursor and pagination.cursor:
            return self._cursor_paginated_response_types(query, pagination)
        else:
            return self._offset_paginated_response_types(query, count_query, pagination, filters or {}, search or "")
    
    def count_lookup_types(self, active_only: bool = True) -> int:
        """Count lookup types."""
        query = self.db.query(PDCLookupType)
        if active_only:
            query = query.filter(PDCLookupType.is_active == True)
        return query.count()
    
    def update_lookup_type(self, lookup_type: str, display_name: str = None, 
                          description: str = None, is_active: bool = None,
                          modified_by: str = "system") -> Optional[PDCLookupType]:
        """Update an existing lookup type."""
        db_lookup_type = self.get_lookup_type(lookup_type)
        if not db_lookup_type:
            return None
        
        if display_name is not None:
            db_lookup_type.display_name = display_name
        if description is not None:
            db_lookup_type.description = description
        if is_active is not None:
            db_lookup_type.is_active = is_active
        
        db_lookup_type.modified_by = modified_by
        db_lookup_type.modified_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(db_lookup_type)
        return db_lookup_type
    
    def delete_lookup_type(self, lookup_type: str) -> bool:
        """Delete a lookup type and all its associated codes."""
        db_lookup_type = self.get_lookup_type(lookup_type)
        if not db_lookup_type:
            return False
        
        # Delete associated lookup codes first
        self.db.query(PDCLookupCode).filter(
            PDCLookupCode.lookup_type == lookup_type
        ).delete()
        
        # Delete the lookup type
        self.db.delete(db_lookup_type)
        self.db.commit()
        return True

    # ========================================
    # LOOKUP CODES CRUD OPERATIONS
    # ========================================
    
    def create_lookup_code(self, lookup_code_data: PDCLookupCodeCreate) -> PDCLookupCode:
        """Create a new lookup code."""
        db_lookup_code = PDCLookupCode(
            lookup_type=lookup_code_data.lookup_type,
            lookup_code=lookup_code_data.lookup_code,
            display_name=lookup_code_data.display_name,
            description=lookup_code_data.description,
            sort_order=lookup_code_data.sort_order,
            created_by=lookup_code_data.created_by,
            created_at=datetime.now(),
            is_active=lookup_code_data.is_active
        )
        self.db.add(db_lookup_code)
        self.db.commit()
        self.db.refresh(db_lookup_code)
        return db_lookup_code
    
    def get_lookup_code(self, lookup_type: str, lookup_code: str) -> Optional[PDCLookupCode]:
        """Get a specific lookup code."""
        return self.db.query(PDCLookupCode).filter(
            and_(
                PDCLookupCode.lookup_type == lookup_type,
                PDCLookupCode.lookup_code == lookup_code
            )
        ).first()
    
    def get_lookup_codes_by_type(self, lookup_type: str, active_only: bool = True, skip: int = 0, limit: int = None) -> List[PDCLookupCode]:
        """Get all lookup codes for a specific type with simple pagination."""
        query = self.db.query(PDCLookupCode).filter(PDCLookupCode.lookup_type == lookup_type)
        if active_only:
            query = query.filter(PDCLookupCode.is_active == True)
        
        # Handle sort_order - put NULL values at the end, then sort by lookup_code
        query = query.order_by(
            PDCLookupCode.sort_order.asc(),
            PDCLookupCode.lookup_code
        )
        
        if skip > 0:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
            
        return query.all()
    
    def get_lookup_codes_paginated(
        self,
        pagination: PaginationRequest,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Get lookup codes with advanced pagination support."""
        
        # Build base query
        query = self._build_base_query_codes(filters, search, include_inactive)
        
        # Build count query for total records  
        count_query = self._build_base_query_codes(filters, search, include_inactive)
        
        # Choose pagination strategy
        if pagination.use_cursor and pagination.cursor:
            return self._cursor_paginated_response_codes(query, pagination)
        else:
            return self._offset_paginated_response_codes(query, count_query, pagination, filters or {}, search or "")
    
    def get_by_type_paginated(
        self,
        lookup_type: str,
        pagination: PaginationRequest,
        search: Optional[str] = None,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Get lookup codes for a specific type with pagination."""
        filters = {'lookup_type': lookup_type}
        return self.get_lookup_codes_paginated(pagination, filters, search, include_inactive)
    
    def count_lookup_codes_by_type(self, lookup_type: str, active_only: bool = True) -> int:
        """Count lookup codes for a specific type."""
        query = self.db.query(PDCLookupCode).filter(PDCLookupCode.lookup_type == lookup_type)
        if active_only:
            query = query.filter(PDCLookupCode.is_active == True)
        return query.count()
    
    def update_lookup_code(self, lookup_type: str, lookup_code: str, display_name: str = None,
                          description: str = None, is_active: bool = None, sort_order: int = None,
                          modified_by: str = "system") -> Optional[PDCLookupCode]:
        """Update an existing lookup code."""
        db_lookup_code = self.get_lookup_code(lookup_type, lookup_code)
        if not db_lookup_code:
            return None
        
        if display_name is not None:
            db_lookup_code.display_name = display_name
        if description is not None:
            db_lookup_code.description = description
        if is_active is not None:
            db_lookup_code.is_active = is_active
        if sort_order is not None:
            db_lookup_code.sort_order = sort_order
        
        db_lookup_code.modified_by = modified_by
        db_lookup_code.modified_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(db_lookup_code)
        return db_lookup_code
    
    def delete_lookup_code(self, lookup_type: str, lookup_code: str) -> bool:
        """Delete a lookup code."""
        db_lookup_code = self.get_lookup_code(lookup_type, lookup_code)
        if not db_lookup_code:
            return False
        
        self.db.delete(db_lookup_code)
        self.db.commit()
        return True

    # ========================================
    # ADVANCED PAGINATION RESPONSES
    # ========================================
    
    def _offset_paginated_response_types(
        self, 
        query, 
        count_query, 
        pagination: PaginationRequest,
        filters: Dict[str, Any],
        search: str
    ) -> Dict[str, Any]:
        """Create offset-based paginated response for lookup types."""
        
        # Apply pagination
        items, pagination_response = AdvancedPagination.offset_pagination(
            query=query,
            model_class=PDCLookupType,
            pagination=pagination,
            count_query=count_query
        )
        
        # Serialize items using model's to_dict() method
        serialized_items = [self.to_api_dict_type(item) for item in items]
        
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "filters_applied": filters,
            "sort_info": {
                "sort_by": pagination.sort_by,
                "sort_order": pagination.sort_order.value
            },
            "search_applied": search
        }
    
    def _offset_paginated_response_codes(
        self, 
        query, 
        count_query, 
        pagination: PaginationRequest,
        filters: Dict[str, Any],
        search: str
    ) -> Dict[str, Any]:
        """Create offset-based paginated response for lookup codes."""
        
        # Apply pagination
        items, pagination_response = AdvancedPagination.offset_pagination(
            query=query,
            model_class=PDCLookupCode,
            pagination=pagination,
            count_query=count_query
        )
        
        # Serialize items using model's to_dict() method
        serialized_items = [self.to_api_dict_code(item) for item in items]
        
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "filters_applied": filters,
            "sort_info": {
                "sort_by": pagination.sort_by,
                "sort_order": pagination.sort_order.value
            },
            "search_applied": search
        }
    
    def _cursor_paginated_response_types(
        self, 
        query, 
        pagination: PaginationRequest
    ) -> Dict[str, Any]:
        """Create cursor-based paginated response for lookup types."""
        
        # Determine cursor field and value
        cursor_field = getattr(PDCLookupType, pagination.sort_by, PDCLookupType.lookup_type)
        cursor_value = pagination.cursor
        
        # Apply cursor pagination
        items, next_cursor, previous_cursor = AdvancedPagination.cursor_pagination(
            query=query,
            model_class=PDCLookupType,
            cursor_field=cursor_field,
            cursor_value=cursor_value,
            limit=pagination.size,
            sort_order=SortOrder.ASC  # Use ascending for lookup types
        )
        
        # Create pagination response
        pagination_response = PaginationResponse.from_cursor_pagination(
            page=pagination.page,
            size=pagination.size,
            total=-1,  # Not calculated for cursor pagination (performance)
            next_cursor=next_cursor,
            previous_cursor=previous_cursor
        )
        
        # Serialize items using model's to_dict() method
        serialized_items = [self.to_api_dict_type(item) for item in items]
        
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "sort_info": {
                "sort_by": cursor_field.name if hasattr(cursor_field, 'name') else 'lookup_type',
                "sort_order": "asc",
                "pagination_type": "cursor"
            }
        }
    
    def _cursor_paginated_response_codes(
        self, 
        query, 
        pagination: PaginationRequest
    ) -> Dict[str, Any]:
        """Create cursor-based paginated response for lookup codes."""
        
        # Determine cursor field and value
        cursor_field = getattr(PDCLookupCode, pagination.sort_by, PDCLookupCode.lookup_code)
        cursor_value = pagination.cursor
        
        # Apply cursor pagination
        items, next_cursor, previous_cursor = AdvancedPagination.cursor_pagination(
            query=query,
            model_class=PDCLookupCode,
            cursor_field=cursor_field,
            cursor_value=cursor_value,
            limit=pagination.size,
            sort_order=SortOrder.ASC  # Use ascending for lookup codes
        )
        
        # Create pagination response
        pagination_response = PaginationResponse.from_cursor_pagination(
            page=pagination.page,
            size=pagination.size,
            total=-1,  # Not calculated for cursor pagination (performance)
            next_cursor=next_cursor,
            previous_cursor=previous_cursor
        )
        
        # Serialize items using model's to_dict() method
        serialized_items = [self.to_api_dict_code(item) for item in items]
        
        return {
            "items": serialized_items,
            "pagination": pagination_response.model_dump(),
            "sort_info": {
                "sort_by": cursor_field.name if hasattr(cursor_field, 'name') else 'lookup_code',
                "sort_order": "asc",
                "pagination_type": "cursor"
            }
        }

    # ========================================
    # UTILITY AND SUMMARY OPERATIONS
    # ========================================
    
    def search_lookup_codes(self, search_term: str, lookup_type: str = None, 
                           active_only: bool = True, limit: int = 100) -> List[PDCLookupCode]:
        """Search lookup codes by term."""
        query = self.db.query(PDCLookupCode)
        
        if active_only:
            query = query.filter(PDCLookupCode.is_active == True)
        
        if lookup_type:
            query = query.filter(PDCLookupCode.lookup_type == lookup_type)
        
        # Case-insensitive search across relevant fields
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                PDCLookupCode.display_name.ilike(search_pattern),
                PDCLookupCode.lookup_code.ilike(search_pattern),
                PDCLookupCode.description.like(search_pattern)  # Simple LIKE for TEXT fields
            )
        )
        
        return query.order_by(
            PDCLookupCode.lookup_type,
            PDCLookupCode.lookup_code
        ).limit(limit).all()
    
    def get_lookup_hierarchy(self) -> Dict[str, List[PDCLookupCode]]:
        """Get complete lookup hierarchy organized by type."""
        lookup_types = self.get_all_lookup_types(active_only=True)
        hierarchy = {}
        
        for lookup_type in lookup_types:
            codes = self.get_lookup_codes_by_type(lookup_type.lookup_type, active_only=True)
            hierarchy[lookup_type.lookup_type] = codes
        
        return hierarchy
    
    def get_lookup_stats(self) -> Dict[str, Any]:
        """Get statistics about lookup tables."""
        # Count lookup types
        total_types = self.db.query(PDCLookupType).count()
        active_types = self.db.query(PDCLookupType).filter(PDCLookupType.is_active == True).count()
        
        # Count lookup codes
        total_codes = self.db.query(PDCLookupCode).count()
        active_codes = self.db.query(PDCLookupCode).filter(PDCLookupCode.is_active == True).count()
        
        return {
            'lookup_types': {
                'total': total_types,
                'active': active_types,
                'inactive': total_types - active_types
            },
            'lookup_codes': {
                'total': total_codes,
                'active': active_codes,
                'inactive': total_codes - active_codes
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def get_types_summary(self) -> Dict[str, Any]:
        """Get summary statistics for lookup types."""
        base_query = self._build_base_query_types(include_inactive=False)
        
        # Total count
        total_count = base_query.count()
        
        # Count by activity status
        active_count = base_query.filter(PDCLookupType.is_active == True).count()
        
        # Get type distribution
        type_stats = {}
        types = base_query.all()
        
        for lookup_type in types:
            code_count = self.count_lookup_codes_by_type(lookup_type.lookup_type, active_only=True)
            type_stats[lookup_type.lookup_type] = {
                'display_name': lookup_type.display_name,
                'active_codes': code_count,
                'created_at': lookup_type.created_at.isoformat() if lookup_type.created_at else None
            }
        
        return {
            "total_types": total_count,
            "active_types": active_count,
            "type_details": type_stats
        }


# ========================================
# QUERY PARAMETER PARSERS
# ========================================

class LookupPaginationQueryParser:
    """Utility class for parsing lookup query parameters into structured formats."""
    
    @staticmethod
    def parse_pagination_params(request_params: Dict[str, str]) -> PaginationRequest:
        """Parse pagination parameters from request."""
        # Determine pagination type based on use_cursor parameter
        use_cursor = request_params.get('use_cursor', 'false').lower() == 'true'
        pagination_type = PaginationType.CURSOR if use_cursor else PaginationType.OFFSET
        
        return PaginationRequest(
            page=int(request_params.get('page', 1)),
            size=int(request_params.get('size', 20)),
            sort_by=request_params.get('sort_by', 'lookup_code'),
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
        for param in ['lookup_type', 'lookup_code']:
            if param in request_params and request_params[param]:
                filters[param] = request_params[param]
        
        # Numeric parameters
        for param in ['sort_order_min', 'sort_order_max']:
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