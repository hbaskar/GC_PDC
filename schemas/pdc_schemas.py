"""
Pydantic schemas for PDC Classification API.
Based on actual database table structure from CMSDEVDB.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class PDCClassificationBase(BaseModel):
    """Base schema for PDC Classification."""
    name: str = Field(..., min_length=1, max_length=100, description="Classification name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique classification code")
    description: Optional[str] = Field(None, max_length=250, description="Classification description")
    old_classification_id: Optional[str] = Field(None, max_length=50, description="Legacy classification ID")
    retention_policy_id: int = Field(..., description="Associated retention policy ID")
    condition_event: Optional[str] = Field(None, max_length=100, description="Trigger event for retention")
    condition_offset_days: Optional[int] = Field(None, description="Offset days for retention condition")
    condition_type: Optional[str] = Field(None, max_length=50, description="Type of retention condition")
    destruction_method: Optional[str] = Field(None, max_length=50, description="Method of destruction")
    condition: Optional[str] = Field(None, max_length=100, description="Additional retention condition")
    vital: Optional[str] = Field(None, max_length=1, description="Vital record indicator (Y/N)")
    citation: Optional[str] = Field(None, max_length=100, description="Legal citation")
    see: Optional[str] = Field(None, max_length=100, description="Reference to other documents")
    file_type: Optional[str] = Field(None, max_length=20, description="File type")
    series: Optional[str] = Field(None, max_length=100, description="Document series")
    classification_level: Optional[str] = Field(None, max_length=50, description="Security classification level")
    sensitivity_rating: Optional[int] = Field(None, ge=1, le=5, description="Sensitivity rating (1-5)")
    media_type: Optional[str] = Field(None, max_length=50, description="Media type")
    template_id: Optional[int] = Field(None, description="Associated template ID")
    classification_purpose: Optional[str] = Field(None, max_length=100, description="Purpose of classification")
    requires_tax_clearance: Optional[bool] = Field(None, description="Requires tax clearance")
    label_format: Optional[str] = Field(None, max_length=100, description="Label format")
    secure: Optional[str] = Field(None, max_length=1, description="Secure flag (Y/N)")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    organization_id: int = Field(..., description="Organization ID")
    record_owner_id: Optional[int] = Field(None, description="Record owner user ID")
    record_owner: Optional[str] = Field(None, max_length=100, description="Record owner name")
    is_active: bool = Field(True, description="Whether the classification is active")

class PDCClassificationCreate(PDCClassificationBase):
    """Schema for creating a new PDC Classification."""
    created_by: str = Field(..., max_length=100, description="User who created the record")

class PDCClassificationUpdate(BaseModel):
    """Schema for updating a PDC Classification."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Classification name")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique classification code")
    description: Optional[str] = Field(None, max_length=250, description="Classification description")
    old_classification_id: Optional[str] = Field(None, max_length=50, description="Legacy classification ID")
    retention_policy_id: Optional[int] = Field(None, description="Associated retention policy ID")
    condition_event: Optional[str] = Field(None, max_length=100, description="Trigger event for retention")
    condition_offset_days: Optional[int] = Field(None, description="Offset days for retention condition")
    condition_type: Optional[str] = Field(None, max_length=50, description="Type of retention condition")
    destruction_method: Optional[str] = Field(None, max_length=50, description="Method of destruction")
    condition: Optional[str] = Field(None, max_length=100, description="Additional retention condition")
    vital: Optional[str] = Field(None, max_length=1, description="Vital record indicator (Y/N)")
    citation: Optional[str] = Field(None, max_length=100, description="Legal citation")
    see: Optional[str] = Field(None, max_length=100, description="Reference to other documents")
    file_type: Optional[str] = Field(None, max_length=20, description="File type")
    series: Optional[str] = Field(None, max_length=100, description="Document series")
    classification_level: Optional[str] = Field(None, max_length=50, description="Security classification level")
    sensitivity_rating: Optional[int] = Field(None, ge=1, le=5, description="Sensitivity rating (1-5)")
    media_type: Optional[str] = Field(None, max_length=50, description="Media type")
    template_id: Optional[int] = Field(None, description="Associated template ID")
    classification_purpose: Optional[str] = Field(None, max_length=100, description="Purpose of classification")
    requires_tax_clearance: Optional[bool] = Field(None, description="Requires tax clearance")
    label_format: Optional[str] = Field(None, max_length=100, description="Label format")
    secure: Optional[str] = Field(None, max_length=1, description="Secure flag (Y/N)")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    organization_id: Optional[int] = Field(None, description="Organization ID")
    record_owner_id: Optional[int] = Field(None, description="Record owner user ID")
    record_owner: Optional[str] = Field(None, max_length=100, description="Record owner name")
    is_active: Optional[bool] = Field(None, description="Whether the classification is active")
    modified_by: Optional[str] = Field(None, max_length=100, description="User who modified the record")

class PDCClassificationResponse(PDCClassificationBase):
    """Schema for PDC Classification response."""
    classification_id: int
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    is_deleted: bool = False
    last_accessed_at: Optional[datetime] = None
    last_accessed_by: Optional[str] = None
    
    model_config = {"from_attributes": True}

class PDCClassificationList(BaseModel):
    """Schema for paginated PDC Classification list."""
    items: List[PDCClassificationResponse]
    total: int
    page: int
    size: int
    pages: int

class PDCClassificationSummary(BaseModel):
    """Schema for simplified classification summary."""
    classification_id: int
    name: str
    code: str
    classification_level: Optional[str] = None
    sensitivity_rating: Optional[int] = None
    is_active: bool = True
    
    model_config = {"from_attributes": True}

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    status_code: int