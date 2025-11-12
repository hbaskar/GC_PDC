"""
PDC Lookup Type model.
Represents the main lookup categories like CLASSIFICATION_LEVEL, MEDIA_TYPE, etc.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from .base import Base


class PDCLookupType(Base):
    """
    Model for pdc_lookup_types table.
    Represents the main lookup categories like CLASSIFICATION_LEVEL, MEDIA_TYPE, etc.
    """
    __tablename__ = 'pdc_lookup_types'
    
    # Primary key
    lookup_type = Column(String(50), primary_key=True, nullable=False)
    
    # Core fields
    display_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)
    
    # Audit fields
    created_at = Column(DateTime, nullable=True, default=func.getdate())
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime, nullable=True)
    modified_by = Column(String(100), nullable=True)
    
    # Relationship to lookup codes
    lookup_codes = relationship("PDCLookupCode", back_populates="lookup_type_ref", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PDCLookupType(lookup_type='{self.lookup_type}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'lookup_type': self.lookup_type,
            'display_name': self.display_name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by
        }