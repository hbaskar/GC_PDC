"""
PDC Template Field model.
Manages fields within templates.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from .base import Base


class PDCTemplateField(Base):
    """Model for pdc_template_fields table."""
    __tablename__ = "pdc_template_fields"
    
    template_field_id = Column(Integer, primary_key=True, nullable=False)
    template_id = Column(Integer, ForeignKey("pdc_templates.template_id"), nullable=False)
    metadata_key = Column(String(100), nullable=False, index=True)
    display_name = Column(String(100))
    data_type = Column(String(50))
    is_required = Column(Boolean, nullable=False, server_default=text('((0))'))
    default_value = Column(String(250))
    validation_rule = Column(String(250))
    sort_order = Column(Integer)
    is_active = Column(Boolean, nullable=False, server_default=text('((1))'))
    created_at = Column(DateTime, nullable=False, server_default=func.getdate())
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime)
    modified_by = Column(String(100))
    
    # Relationships
    template = relationship("PDCTemplate", back_populates="template_fields")
    
    def __repr__(self):
        return f"<PDCTemplateField(id={self.template_field_id}, key='{self.metadata_key}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'template_field_id': self.template_field_id,
            'template_id': self.template_id,
            'metadata_key': self.metadata_key,
            'display_name': self.display_name,
            'data_type': self.data_type,
            'is_required': self.is_required,
            'default_value': self.default_value,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by
        }