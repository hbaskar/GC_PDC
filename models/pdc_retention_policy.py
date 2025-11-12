"""
PDC Retention Policy model.
Manages retention policies for classifications.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from .base import Base


class PDCRetentionPolicy(Base):
    """Model for pdc_retention_policies table."""
    __tablename__ = "pdc_retention_policies"
    
    retention_policy_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(250))
    retention_code = Column(String(50))
    retention_type = Column(String(50))
    trigger_event = Column(String(50))
    retention_period_days = Column(Integer, nullable=False)
    applicable_data_types = Column(String(250))
    jurisdiction = Column(String(100))
    legal_basis = Column(String(250))
    disposition_method = Column(String(100))
    review_frequency = Column(String(50))
    policy_owner = Column(String(100))
    audit_required = Column(Boolean, nullable=False, server_default=text('((0))'))
    exceptions = Column(String(250))
    version = Column(String(20))
    destruction_method = Column(String(100))
    is_active = Column(Boolean, nullable=False, server_default=text('((1))'))
    comments = Column(String(250))
    created_at = Column(DateTime, nullable=False, server_default=func.getdate())
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime)
    modified_by = Column(String(100))
    
    # Relationships
    classifications = relationship("PDCClassification", back_populates="retention_policy")
    
    def __repr__(self):
        return f"<PDCRetentionPolicy(id={self.retention_policy_id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'retention_policy_id': self.retention_policy_id,
            'name': self.name,
            'description': self.description,
            'retention_code': self.retention_code,
            'retention_period_days': self.retention_period_days,
            'disposition_method': self.disposition_method,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by
        }