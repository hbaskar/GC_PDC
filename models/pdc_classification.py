"""
PDC Classification model.
Main classification entity for the PDC (Product Data Classification) system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from .base import Base


class PDCClassification(Base):
    """Model for pdc_classifications table."""
    __tablename__ = "pdc_classifications"
    
    classification_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    description = Column(String(250))
    old_classification_id = Column(String(50))
    retention_policy_id = Column(Integer, ForeignKey("pdc_retention_policies.retention_policy_id"), nullable=False)
    
    condition_event = Column(String(100))
    condition_offset_days = Column(Integer)
    condition_type = Column(String(50))
    destruction_method = Column(String(50))
    condition = Column(String(100))
    vital = Column(String(1))
    citation = Column(String(100))
    see = Column(String(100))
    file_type = Column(String(20))
    series = Column(String(100))
    classification_level = Column(String(50), index=True)
    sensitivity_rating = Column(Integer)
    media_type = Column(String(50))
    template_id = Column(Integer, ForeignKey("pdc_templates.template_id"))
    classification_purpose = Column(String(100))
    requires_tax_clearance = Column(Boolean, server_default=text('((0))'))
    label_format = Column(String(100))
    secure = Column(String(1))
    effective_date = Column(DateTime)
    organization_id = Column(Integer, ForeignKey("pdc_organizations.organization_id"), nullable=False)
    record_owner_id = Column(Integer)
    record_owner = Column(String(100))
    is_active = Column(Boolean, nullable=False, server_default=text('((1))'))
    created_at = Column(DateTime, nullable=False, server_default=func.getdate())
    created_by = Column(String(100), nullable=False)
    modified_at = Column(DateTime)
    modified_by = Column(String(100))
    deleted_at = Column(DateTime)
    deleted_by = Column(String(100))
    is_deleted = Column(Boolean, nullable=False, server_default=text('((0))'))
    last_accessed_at = Column(DateTime)
    last_accessed_by = Column(String(100))
    
    # Relationships
    retention_policy = relationship("PDCRetentionPolicy", back_populates="classifications")
    template = relationship("PDCTemplate", back_populates="classifications")
    organization = relationship("PDCOrganization", back_populates="classifications")
    
    def __repr__(self):
        return f"<PDCClassification(id={self.classification_id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary with all database columns."""
        base_dict = {
            # Primary identifiers
            'classification_id': self.classification_id,
            'classification_code': self.code,  # API-friendly field name
            'name': self.name,
            'description': self.description,
            'old_classification_id': self.old_classification_id,
            
            # Retention and policy fields
            'retention_policy_id': self.retention_policy_id,
            'condition_event': self.condition_event,
            'condition_offset_days': self.condition_offset_days,
            'condition_type': self.condition_type,
            'destruction_method': self.destruction_method,
            'condition': self.condition,
            'vital': self.vital,
            'citation': self.citation,
            'see': self.see,
            
            # Classification attributes
            'file_type': self.file_type,
            'series': self.series,
            'classification_level': self.classification_level,
            'sensitivity_rating': self.sensitivity_rating,
            'media_type': self.media_type,
            'template_id': self.template_id,
            'classification_purpose': self.classification_purpose,
            'requires_tax_clearance': self.requires_tax_clearance,
            'label_format': self.label_format,
            'secure': self.secure,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            
            # Organizational fields
            'organization_id': self.organization_id,
            'record_owner_id': self.record_owner_id,
            'record_owner': self.record_owner,
            
            # Status and lifecycle fields
            'is_active': self.is_active,
            'status': 'active' if self.is_active else 'inactive',  # API-friendly status
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'deleted_by': self.deleted_by,
            'is_deleted': self.is_deleted,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'last_accessed_by': self.last_accessed_by,
        }
        
        # Add retention policy fields through relationship
        if self.retention_policy:
            retention_dict = {
                'retention_code': self.retention_policy.retention_code,
                'retention_type': self.retention_policy.retention_type,
                'trigger_event': self.retention_policy.trigger_event,
                'min_retention_years': self.retention_policy.retention_period_days // 365 if self.retention_policy.retention_period_days else None,
                'max_retention_years': (self.retention_policy.retention_period_days // 365) + 2 if self.retention_policy.retention_period_days else None,  # Estimate max as min + 2
                'legal_hold_flag': False,  # Default value, could be enhanced later
                'destruction_method': self.retention_policy.destruction_method,
                'review_frequency': self.retention_policy.review_frequency
            }
            base_dict.update(retention_dict)
        else:
            # Provide default values if no retention policy is linked
            base_dict.update({
                'retention_code': None,
                'retention_type': None,
                'trigger_event': None,
                'min_retention_years': None,
                'max_retention_years': None,
                'legal_hold_flag': False,
                'destruction_method': None,
                'review_frequency': None
            })
        
        return base_dict
