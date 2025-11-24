"""
Advanced Server-Level Paging Implementation Guide

This module demonstrates comprehensive server-level paging strategies for GET endpoints
with performance optimizations, cursor-based paging, and flexible sorting.
"""
from typing import Optional, List, Tuple, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc, func, text
from pydantic import BaseModel, Field, validator
from enum import Enum

class SortOrder(str, Enum):
    """Sort order enumeration."""
    ASC = "asc"
    DESC = "desc"

class PaginationType(str, Enum):
    """Pagination type enumeration."""
    OFFSET = "offset"  # Traditional offset/limit paging
    CURSOR = "cursor"  # Cursor-based paging for better performance

class PaginationRequest(BaseModel):
    """Standardized pagination request model."""
    
    # Offset-based pagination
    page: int = Field(default=1, ge=1, le=10000, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    # Cursor-based pagination  
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")
    
    # Pagination type
    pagination_type: PaginationType = Field(default=PaginationType.OFFSET, description="Type of pagination")
    
    @validator('size')
    def validate_size(cls, v):
        """Ensure reasonable page sizes for performance."""
        if v > 100:
            raise ValueError("Page size cannot exceed 100 items")
        return v
    
    @property
    def skip(self) -> int:
        """Calculate skip/offset value."""
        return (self.page - 1) * self.size
    
    @property
    def use_cursor(self) -> bool:
        """Check if cursor-based pagination should be used."""
        return self.pagination_type == PaginationType.CURSOR

class PaginationResponse(BaseModel):
    """Standardized pagination response model."""
    
    # Current page info
    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    total: int = Field(description="Total number of items")
    pages: int = Field(description="Total number of pages")
    
    # Navigation info
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for next page")
    previous_cursor: Optional[str] = Field(default=None, description="Cursor for previous page")
    
    # Performance info
    query_time_ms: Optional[float] = Field(default=None, description="Query execution time in milliseconds")
    
    @classmethod
    def from_offset_pagination(
        cls, 
        page: int, 
        size: int, 
        total: int, 
        query_time_ms: Optional[float] = None
    ) -> 'PaginationResponse':
        """Create pagination response from offset-based pagination."""
        pages = (total + size - 1) // size  # Ceiling division
        
        return cls(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_next=page < pages,
            has_previous=page > 1,
            query_time_ms=query_time_ms
        )
    
    @classmethod
    def from_cursor_pagination(
        cls,
        page: int,
        size: int,
        total: int,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        query_time_ms: Optional[float] = None
    ) -> 'PaginationResponse':
        """Create pagination response from cursor-based pagination."""
        return cls(
            page=page,
            size=size,
            total=total,
            pages=-1,  # Not applicable for cursor pagination
            has_next=next_cursor is not None,
            has_previous=previous_cursor is not None,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            query_time_ms=query_time_ms
        )

class PaginatedResult(BaseModel):
    """Generic paginated result container."""
    
    items: List[Dict[str, Any]] = Field(description="The paginated items")
    pagination: PaginationResponse = Field(description="Pagination metadata")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    sort_info: Dict[str, str] = Field(default_factory=dict, description="Sorting information")

class AdvancedPagination:
    """
    Advanced pagination utility class with multiple strategies.
    
    Supports both offset-based and cursor-based pagination with performance optimizations.
    """
    
    @staticmethod
    def get_sortable_columns(model_class) -> List[str]:
        """Get list of sortable columns for a model."""
        return [column.name for column in model_class.__table__.columns]
    
    @staticmethod
    def apply_sorting(
        query: Query, 
        model_class,
        sort_by: str = "created_at",
        sort_order: SortOrder = SortOrder.DESC
    ) -> Query:
        """Apply sorting to a query with validation."""
        
        # Validate sort column exists
        sortable_columns = AdvancedPagination.get_sortable_columns(model_class)
        if sort_by not in sortable_columns:
            sort_by = "created_at"  # Fallback to safe default
        
        # Get the column attribute
        sort_column = getattr(model_class, sort_by)
        
        # Apply sort order
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        return query
    
    @staticmethod
    def offset_pagination(
        query: Query,
        model_class,
        pagination: PaginationRequest,
        count_query: Optional[Query] = None
    ) -> Tuple[List, PaginationResponse]:
        """
        Perform offset-based pagination with optimizations.
        
        Args:
            query: Base SQLAlchemy query
            model_class: The model class for sorting validation
            pagination: Pagination parameters
            count_query: Optional separate query for counting (optimization)
        
        Returns:
            Tuple of (items, pagination_response)
        """
        start_time = datetime.now()
        
        # Apply sorting
        query = AdvancedPagination.apply_sorting(
            query, model_class, pagination.sort_by, pagination.sort_order
        )
        
        # Get total count (use separate query if provided for optimization)
        if count_query is not None:
            total = count_query.count()
        else:
            total = query.count()
        
        # Apply pagination
        items = query.offset(pagination.skip).limit(pagination.size).all()
        
        # Calculate query time
        end_time = datetime.now()
        query_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Create pagination response
        pagination_response = PaginationResponse.from_offset_pagination(
            page=pagination.page,
            size=pagination.size,
            total=total,
            query_time_ms=query_time_ms
        )
        
        return items, pagination_response
    
    @staticmethod
    def cursor_pagination(
        query: Query,
        model_class,
        cursor_field: str = "id",
        cursor_value: Optional[Union[int, str, datetime]] = None,
        limit: int = 20,
        sort_order: SortOrder = SortOrder.ASC
    ) -> Tuple[List, Optional[str], Optional[str]]:
        """
        Perform cursor-based pagination for better performance on large datasets.
        
        Args:
            query: Base SQLAlchemy query
            model_class: The model class
            cursor_field: Field to use for cursor (should be indexed and unique/sequential)
            cursor_value: Current cursor value
            limit: Number of items to return
            sort_order: Sort order for cursor field
        
        Returns:
            Tuple of (items, next_cursor, previous_cursor)
        """
        start_time = datetime.now()
        
        # Get the cursor column
        cursor_column = getattr(model_class, cursor_field)
        
        # Apply cursor filter if provided
        if cursor_value is not None:
            if sort_order == SortOrder.ASC:
                query = query.filter(cursor_column >= cursor_value)
            else:
                query = query.filter(cursor_column <= cursor_value)
        
        # Apply sorting by cursor field
        if sort_order == SortOrder.ASC:
            query = query.order_by(asc(cursor_column))
        else:
            query = query.order_by(desc(cursor_column))
        
        # Fetch one extra item to check if there's a next page
        items = query.limit(limit + 1).all()
        
        # Determine if there are more pages
        has_next = len(items) > limit
        if has_next:
            # Save the extra item for cursor
            extra_item = items[-1]
            items = items[:-1]  # Remove extra item
        else:
            extra_item = None

        # Generate cursors
        next_cursor = None
        previous_cursor = None

        if has_next and extra_item:
            next_cursor = str(getattr(extra_item, cursor_field))
        if items and cursor_value is not None:
            previous_cursor = str(getattr(items[0], cursor_field))

        return items, next_cursor, previous_cursor

def create_paginated_response(
    items: List,
    pagination_response: PaginationResponse,
    item_schema,
    filters_applied: Dict[str, Any] = None,
    sort_info: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Create a standardized paginated API response.
    
    Args:
        items: List of items to serialize
        pagination_response: Pagination metadata
        item_schema: Pydantic schema for item serialization
        filters_applied: Dictionary of applied filters
        sort_info: Dictionary of sorting information
    
    Returns:
        Standardized paginated response dictionary
    """
    
    # Serialize items
    serialized_items = []
    for item in items:
        if hasattr(item_schema, 'model_validate'):
            # Pydantic v2
            serialized_items.append(item_schema.model_validate(item).model_dump())
        else:
            # Pydantic v1 fallback
            serialized_items.append(item_schema.from_orm(item).dict())
    
    return {
        "items": serialized_items,
        "pagination": pagination_response.dict(),
        "filters_applied": filters_applied or {},
        "sort_info": sort_info or {},
        "meta": {
            "total_items": pagination_response.total,
            "current_page": pagination_response.page,
            "items_per_page": pagination_response.size,
            "total_pages": pagination_response.pages,
            "query_performance": {
                "execution_time_ms": pagination_response.query_time_ms
            }
        }
    }
