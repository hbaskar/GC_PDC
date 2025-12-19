"""
PDC Models Package

This package contains all SQLAlchemy models for the PDC (Product Data Classification) system.
Each model is in its own file for better organization and maintainability.
"""

# Import Base first
from .base import Base


# Import all models
from .pdc_lookup_type import PDCLookupType, PDCLookupTypeView
from .pdc_lookup_code import PDCLookupCode, PDCLookupCodeView
from .pdc_classification import PDCClassification
from .pdc_retention_policy import PDCRetentionPolicy
from .pdc_template import PDCTemplate
from .pdc_template_field import PDCTemplateField
from .pdc_organization import PDCOrganization
from .pdc_library import PDCLibrary

# Export all models
__all__ = [
    # Base
    'Base',
    
    # Models
    'PDCLookupType',
    'PDCLookupTypeView',
    'PDCLookupCode',
    'PDCLookupCodeView',
    'PDCClassification',
    'PDCRetentionPolicy',
    'PDCTemplate',
    'PDCTemplateField',
    'PDCOrganization',
    'PDCLibrary'
]
