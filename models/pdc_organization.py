"""
PDC Organization model.
Manages organization entities.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from .base import Base


class PDCOrganization(Base):
    """Model for pdc_organizations table."""
    __tablename__ = "pdc_organizations"
    
    organization_id = Column(Integer, primary_key=True, nullable=False)
    organization_name = Column(String(100), nullable=False, index=True)
    organization_code = Column(String(50))
    description = Column(String(250))
    parent_organization_id = Column(Integer, ForeignKey("pdc_organizations.organization_id"))
    is_active = Column(Boolean, nullable=False, server_default=text('((1))'))
    created_at = Column(DateTime, nullable=False, server_default=func.getdate())
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime)
    modified_by = Column(String(100))
    
    # Relationships
    classifications = relationship("PDCClassification", back_populates="organization")
    # Self-referential relationship for parent organization
    parent_organization = relationship("PDCOrganization", remote_side=[organization_id])
    
    def __repr__(self):
        return f"<PDCOrganization(id={self.organization_id}, name='{self.organization_name}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'organization_id': self.organization_id,
            'organization_name': self.organization_name,
            'organization_code': self.organization_code,
            'description': self.description,
            'parent_organization_id': self.parent_organization_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by
        }
