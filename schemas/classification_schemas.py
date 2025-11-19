"""
Pydantic schemas for PDC Classification API.
Based on actual database table structure from CMSDEVDB.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class PDCClassificationBase(BaseModel):
    """Base schema for PDC Classification matching the database model exactly."""
    # Primary identifiers - API fields
    classification_code: str = Field(..., min_length=1, max_length=50, description="Unique classification code (maps to 'code' in DB)")
    name: Optional[str] = Field(None, max_length=100, description="Classification name")
    description: Optional[str] = Field(None, max_length=250, description="Classification description")
    old_classification_id: Optional[str] = Field(None, max_length=50, description="Legacy classification ID")
    
    # Required relationships
    retention_policy_id: int = Field(..., description="Associated retention policy ID")
    organization_id: int = Field(..., description="Organization ID")
    
    # Retention condition fields
    condition_event: Optional[str] = Field(None, max_length=100, description="Trigger event for retention")
    condition_offset_days: Optional[int] = Field(None, description="Offset days for retention condition")
    condition_type: Optional[str] = Field(None, max_length=50, description="Type of retention condition")
    destruction_method: Optional[str] = Field(None, max_length=50, description="Method of destruction")
    condition: Optional[str] = Field(None, max_length=100, description="Additional retention condition")
    vital: Optional[str] = Field(None, max_length=1, description="Vital record indicator (Y/N)")
    citation: Optional[str] = Field(None, max_length=100, description="Legal citation")
    see: Optional[str] = Field(None, max_length=100, description="Reference to other documents")
    
    # Classification attributes  
    file_type: Optional[str] = Field(None, max_length=20, description="File type (maps from 'keywords' in API)")
    series: Optional[str] = Field(None, max_length=100, description="Document series (maps from 'doc_types' in API)")
    classification_level: Optional[str] = Field(None, max_length=50, description="Security classification level (maps from 'category' in API)")
    sensitivity_rating: Optional[int] = Field(None, description="Sensitivity rating")
    media_type: Optional[str] = Field(None, max_length=50, description="Media type (maps from 'sub_category' in API)")
    template_id: Optional[int] = Field(None, description="Associated template ID")
    classification_purpose: Optional[str] = Field(None, max_length=100, description="Purpose of classification")
    requires_tax_clearance: Optional[bool] = Field(False, description="Requires tax clearance")
    label_format: Optional[str] = Field(None, max_length=100, description="Label format")
    secure: Optional[str] = Field(None, max_length=1, description="Secure flag (Y/N)")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    
    # Ownership and access
    record_owner_id: Optional[int] = Field(None, description="Record owner user ID")
    record_owner: Optional[str] = Field(None, max_length=100, description="Record owner name")
    
    # Status fields
    is_active: bool = Field(True, description="Whether the classification is active")
    
    # Audit fields (for create, these are auto-populated)
    created_by: Optional[str] = Field(None, max_length=100, description="User who created the record")
    
    # Retention Policy Fields (from relationship - read-only)
    retention_code: Optional[str] = Field(None, max_length=50, description="Retention code")
    retention_type: Optional[str] = Field(None, max_length=50, description="Type of retention")
    trigger_event: Optional[str] = Field(None, max_length=50, description="Event that triggers retention")
    min_retention_years: Optional[int] = Field(None, description="Minimum retention years")
    max_retention_years: Optional[int] = Field(None, description="Maximum retention years")
    legal_hold_flag: Optional[bool] = Field(False, description="Legal hold flag")
    review_frequency: Optional[str] = Field(None, max_length=50, description="How often to review retention")

class PDCClassificationCreate(PDCClassificationBase):
    """Schema for creating a new PDC Classification."""
    pass

class PDCClassificationUpdate(BaseModel):
    """Schema for updating a PDC Classification - all fields optional."""
    # Primary identifiers
    classification_code: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique classification code")
    name: Optional[str] = Field(None, max_length=100, description="Classification name")
    description: Optional[str] = Field(None, max_length=250, description="Classification description")
    old_classification_id: Optional[str] = Field(None, max_length=50, description="Legacy classification ID")
    
    # Relationships
    retention_policy_id: Optional[int] = Field(None, description="Associated retention policy ID")
    organization_id: Optional[int] = Field(None, description="Organization ID")
    
    # Retention condition fields
    condition_event: Optional[str] = Field(None, max_length=100, description="Trigger event for retention")
    condition_offset_days: Optional[int] = Field(None, description="Offset days for retention condition")
    condition_type: Optional[str] = Field(None, max_length=50, description="Type of retention condition")
    destruction_method: Optional[str] = Field(None, max_length=50, description="Method of destruction")
    condition: Optional[str] = Field(None, max_length=100, description="Additional retention condition")
    vital: Optional[str] = Field(None, max_length=1, description="Vital record indicator (Y/N)")
    citation: Optional[str] = Field(None, max_length=100, description="Legal citation")
    see: Optional[str] = Field(None, max_length=100, description="Reference to other documents")
    
    # Classification attributes
    file_type: Optional[str] = Field(None, max_length=20, description="File type")
    series: Optional[str] = Field(None, max_length=100, description="Document series")
    classification_level: Optional[str] = Field(None, max_length=50, description="Security classification level")
    sensitivity_rating: Optional[int] = Field(None, description="Sensitivity rating")
    media_type: Optional[str] = Field(None, max_length=50, description="Media type")
    template_id: Optional[int] = Field(None, description="Associated template ID")
    classification_purpose: Optional[str] = Field(None, max_length=100, description="Purpose of classification")
    requires_tax_clearance: Optional[bool] = Field(None, description="Requires tax clearance")
    label_format: Optional[str] = Field(None, max_length=100, description="Label format")
    secure: Optional[str] = Field(None, max_length=1, description="Secure flag (Y/N)")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    
    # Ownership and access
    record_owner_id: Optional[int] = Field(None, description="Record owner user ID")
    record_owner: Optional[str] = Field(None, max_length=100, description="Record owner name")
    
    # Status fields
    is_active: Optional[bool] = Field(None, description="Whether the classification is active")
    
    # Audit fields
    modified_by: Optional[str] = Field(None, max_length=100, description="User who modified the record")
    
    # Retention Policy Fields (read-only from relationship, but included for completeness)
    retention_code: Optional[str] = Field(None, max_length=50, description="Retention code (read-only)")
    retention_type: Optional[str] = Field(None, max_length=50, description="Type of retention (read-only)")
    trigger_event: Optional[str] = Field(None, max_length=50, description="Event that triggers retention (read-only)")
    min_retention_years: Optional[int] = Field(None, description="Minimum retention years (read-only)")
    max_retention_years: Optional[int] = Field(None, description="Maximum retention years (read-only)")
    legal_hold_flag: Optional[bool] = Field(None, description="Legal hold flag (read-only)")
    review_frequency: Optional[str] = Field(None, max_length=50, description="How often to review retention (read-only)")

class PDCClassificationResponse(BaseModel):
    """
    Schema for PDC Classification response - matches model's to_dict() output exactly.
    Uses model's to_dict() method as the single source of truth.
    """
    # Primary identifiers
    classification_id: Optional[int] = Field(None, description="Primary key")
    classification_code: Optional[str] = Field(None, description="API-friendly field name (maps to 'code')")
    name: Optional[str] = Field(None, description="Classification name")
    description: Optional[str] = Field(None, description="Classification description")
    old_classification_id: Optional[str] = Field(None, description="Legacy classification ID")
    
    # Relationships
    retention_policy_id: Optional[int] = Field(None, description="Associated retention policy ID")
    organization_id: Optional[int] = Field(None, description="Organization ID")
    template_id: Optional[int] = Field(None, description="Associated template ID")
    
    # Retention condition fields
    condition_event: Optional[str] = Field(None, description="Trigger event for retention")
    condition_offset_days: Optional[int] = Field(None, description="Offset days for retention condition")
    condition_type: Optional[str] = Field(None, description="Type of retention condition")
    destruction_method: Optional[str] = Field(None, description="Method of destruction")
    condition: Optional[str] = Field(None, description="Additional retention condition")
    vital: Optional[str] = Field(None, description="Vital record indicator (Y/N)")
    citation: Optional[str] = Field(None, description="Legal citation")
    see: Optional[str] = Field(None, description="Reference to other documents")
    
    # Classification attributes (DB field names)
    file_type: Optional[str] = Field(None, description="File type")
    series: Optional[str] = Field(None, description="Document series")
    classification_level: Optional[str] = Field(None, description="Security classification level")
    sensitivity_rating: Optional[int] = Field(None, description="Sensitivity rating")
    media_type: Optional[str] = Field(None, description="Media type")
    classification_purpose: Optional[str] = Field(None, description="Purpose of classification")
    requires_tax_clearance: Optional[bool] = Field(None, description="Requires tax clearance")
    label_format: Optional[str] = Field(None, description="Label format")
    secure: Optional[str] = Field(None, description="Secure flag (Y/N)")
    effective_date: Optional[str] = Field(None, description="Effective date (ISO format)")
    
    # Ownership and access
    record_owner_id: Optional[int] = Field(None, description="Record owner user ID")
    record_owner: Optional[str] = Field(None, description="Record owner name")
    
    # Status and lifecycle fields (DB format)
    is_active: Optional[bool] = Field(None, description="Whether the classification is active")
    is_deleted: Optional[bool] = Field(None, description="Whether the classification is deleted")
    created_at: Optional[str] = Field(None, description="Creation timestamp (ISO format)")
    created_by: Optional[str] = Field(None, description="User who created the record")
    modified_at: Optional[str] = Field(None, description="Last modification timestamp (ISO format)")
    modified_by: Optional[str] = Field(None, description="User who modified the record")
    deleted_at: Optional[str] = Field(None, description="Deletion timestamp (ISO format)")
    deleted_by: Optional[str] = Field(None, description="User who deleted the record")
    last_accessed_at: Optional[str] = Field(None, description="Last access timestamp (ISO format)")
    last_accessed_by: Optional[str] = Field(None, description="User who last accessed the record")
    
    # API-friendly status field (computed from is_active)
    status: Optional[str] = Field(None, description="API-friendly status (active/inactive)")
    
    # Retention Policy Fields (from relationship)
    retention_code: Optional[str] = Field(None, description="Retention code")
    retention_type: Optional[str] = Field(None, description="Type of retention")
    trigger_event: Optional[str] = Field(None, description="Event that triggers retention")
    min_retention_years: Optional[int] = Field(None, description="Minimum retention years")
    max_retention_years: Optional[int] = Field(None, description="Maximum retention years")
    legal_hold_flag: Optional[bool] = Field(None, description="Legal hold flag")
    review_frequency: Optional[str] = Field(None, description="How often to review retention")
    
    # Template information (computed field)
    template_name: Optional[str] = Field(None, description="Template name (resolved from template_id)")
    
    model_config = {"extra": "allow"}

class PDCClassificationList(BaseModel):
    """Schema for paginated PDC Classification list."""
    items: List[PDCClassificationResponse]
    total: int
    page: int
    size: int
    pages: int

class PDCClassificationSummary(BaseModel):
    """Schema for simplified classification summary."""
    # Primary identifiers
    classification_id: int
    name: str
    classification_code: str
    
    # Key classification attributes  
    classification_level: Optional[str] = None
    sensitivity_rating: Optional[int] = None
    media_type: Optional[str] = None
    file_type: Optional[str] = None
    series: Optional[str] = None
    
    # Status
    is_active: bool = True
    status: Optional[str] = None
    
    # Relationships
    retention_policy_id: Optional[int] = None
    template_id: Optional[int] = None
    organization_id: Optional[int] = None
    
    # Computed/joined fields
    template_name: Optional[str] = Field(None, description="Template name (resolved from template_id)")
    retention_code: Optional[str] = Field(None, description="Retention code from policy")
    
    model_config = {"from_attributes": True}

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    status_code: int
