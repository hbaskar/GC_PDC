"""
PDC Lookup Code model.
Represents individual lookup values within each category.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from .base import Base


class PDCLookupCode(Base):
    """
    Model for pdc_lookup_codes table.
    Represents individual lookup values within each category.
    """
    __tablename__ = 'pdc_lookup_codes'
    
    # Composite primary key
    lookup_type = Column(String(50), ForeignKey('pdc_lookup_types.lookup_type'), primary_key=True, nullable=False)
    lookup_code = Column(String(50), primary_key=True, nullable=False)
    
    # Core fields
    display_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)
    sort_order = Column(Integer, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, nullable=True, default=func.getdate())
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime, nullable=True)
    modified_by = Column(String(100), nullable=True)
    
    # Relationship to lookup type
    lookup_type_ref = relationship("PDCLookupType", back_populates="lookup_codes")
    
    def __repr__(self):
        return f"<PDCLookupCode(lookup_type='{self.lookup_type}', lookup_code='{self.lookup_code}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'lookup_type': self.lookup_type,
            'lookup_code': self.lookup_code,
            'display_name': self.display_name,
            'description': self.description,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by
        }
