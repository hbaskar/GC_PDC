from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PDCTemplate(Base):
    __tablename__ = 'pdc_templates'

    template_id = Column(Integer, primary_key=True, autoincrement=True)
    template_name = Column(String(100), nullable=False)
    description = Column(String(250), nullable=True)
    version = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime, nullable=True)
    modified_by = Column(String(100), nullable=True)

    def to_dict(self):
        return {
            'template_id': self.template_id,
            'template_name': self.template_name,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'created_by': self.created_by,
            'modified_at': self.modified_at,
            'modified_by': self.modified_by,
        }
"""
PDC Template model.
Manages template definitions for classifications.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from .base import Base


class PDCTemplate(Base):
    """Model for pdc_templates table."""
    __tablename__ = "pdc_templates"
    
    template_id = Column(Integer, primary_key=True, nullable=False)
    template_name = Column(String(100), nullable=False, index=True)
    description = Column(String(250))
    version = Column(String(20))
    is_active = Column(Boolean, nullable=False, server_default=text('((1))'))
    created_at = Column(DateTime, nullable=False, server_default=func.getdate())
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime)
    modified_by = Column(String(100))
    
    # Relationships
    classifications = relationship("PDCClassification", back_populates="template")
    template_fields = relationship("PDCTemplateField", back_populates="template")
    
    def __repr__(self):
        return f"<PDCTemplate(id={self.template_id}, name='{self.template_name}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'template_id': self.template_id,
            'template_name': self.template_name,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by
        }
