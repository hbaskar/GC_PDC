"""
CRUD operations for PDC Lookup Tables.
Simple service pattern following the same approach as PDC Classifications.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
from models import PDCLookupType, PDCLookupCode
from schemas.lookup_schemas import (
    PDCLookupTypeCreate, 
    PDCLookupTypeUpdate,
    PDCLookupCodeCreate,
    PDCLookupCodeUpdate
)


class PDCLookupService:
    """Service class for PDC Lookup operations."""
    
    def __init__(self, db: Session):
        self.db = db

    # ========== LOOKUP TYPES OPERATIONS ==========
    
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
        """Get all lookup types with pagination."""
        query = self.db.query(PDCLookupType)
        if active_only:
            query = query.filter(PDCLookupType.is_active == True)
        query = query.order_by(PDCLookupType.lookup_type)
        
        if skip > 0:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
            
        return query.all()
    
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

    # ========== LOOKUP CODES OPERATIONS ==========
    
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
        """Get all lookup codes for a specific type with pagination."""
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

    # ========== UTILITY OPERATIONS ==========
    
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