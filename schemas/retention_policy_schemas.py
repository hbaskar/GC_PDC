"""
Pydantic schemas for PDC Retention Policy API.
Based on actual database table structure from CMSDEVDB.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class PDCRetentionPolicyBase(BaseModel):
    """Base schema for PDC Retention Policy."""
    name: str = Field(..., min_length=1, max_length=100, description="Policy name")
    description: Optional[str] = Field(None, max_length=250, description="Policy description")
    retention_code: Optional[str] = Field(None, max_length=50, description="Unique retention code")
    retention_type: Optional[str] = Field(None, max_length=50, description="Type of retention (Time-based, Event-based)")
    trigger_event: Optional[str] = Field(None, max_length=50, description="Event that triggers retention")
    retention_period_days: int = Field(..., ge=1, description="Retention period in days")
    applicable_data_types: Optional[str] = Field(None, max_length=250, description="Data types this policy applies to")
    jurisdiction: Optional[str] = Field(None, max_length=100, description="Legal jurisdiction")
    legal_basis: Optional[str] = Field(None, max_length=250, description="Legal basis for retention")
    disposition_method: Optional[str] = Field(None, max_length=100, description="Method of disposition")
    review_frequency: Optional[str] = Field(None, max_length=50, description="Review frequency (Annual, Quarterly, etc.)")
    policy_owner: Optional[str] = Field(None, max_length=100, description="Policy owner")
    audit_required: bool = Field(False, description="Whether audit is required")
    exceptions: Optional[str] = Field(None, max_length=250, description="Policy exceptions")
    version: Optional[str] = Field(None, max_length=20, description="Policy version")
    destruction_method: Optional[str] = Field(None, max_length=100, description="Method of destruction")
    comments: Optional[str] = Field(None, max_length=250, description="Additional comments")
    is_active: bool = Field(True, description="Whether the policy is active")

class PDCRetentionPolicyCreate(PDCRetentionPolicyBase):
    """Schema for creating a new PDC Retention Policy."""
    created_by: str = Field(..., max_length=100, description="User who created the policy")

class PDCRetentionPolicyUpdate(BaseModel):
    """Schema for updating a PDC Retention Policy."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Policy name")
    description: Optional[str] = Field(None, max_length=250, description="Policy description")
    retention_code: Optional[str] = Field(None, max_length=50, description="Unique retention code")
    retention_type: Optional[str] = Field(None, max_length=50, description="Type of retention")
    trigger_event: Optional[str] = Field(None, max_length=50, description="Event that triggers retention")
    retention_period_days: Optional[int] = Field(None, ge=1, description="Retention period in days")
    applicable_data_types: Optional[str] = Field(None, max_length=250, description="Data types this policy applies to")
    jurisdiction: Optional[str] = Field(None, max_length=100, description="Legal jurisdiction")
    legal_basis: Optional[str] = Field(None, max_length=250, description="Legal basis for retention")
    disposition_method: Optional[str] = Field(None, max_length=100, description="Method of disposition")
    review_frequency: Optional[str] = Field(None, max_length=50, description="Review frequency")
    policy_owner: Optional[str] = Field(None, max_length=100, description="Policy owner")
    audit_required: Optional[bool] = Field(None, description="Whether audit is required")
    exceptions: Optional[str] = Field(None, max_length=250, description="Policy exceptions")
    version: Optional[str] = Field(None, max_length=20, description="Policy version")
    destruction_method: Optional[str] = Field(None, max_length=100, description="Method of destruction")
    comments: Optional[str] = Field(None, max_length=250, description="Additional comments")
    is_active: Optional[bool] = Field(None, description="Whether the policy is active")
    modified_by: Optional[str] = Field(None, max_length=100, description="User who modified the policy")

class PDCRetentionPolicyResponse(PDCRetentionPolicyBase):
    """Schema for PDC Retention Policy response."""
    retention_policy_id: int = Field(..., description="Retention policy ID")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    modified_at: Optional[str] = Field(None, description="Last modification timestamp")
    created_by: Optional[str] = Field(None, description="User who created the policy")
    modified_by: Optional[str] = Field(None, description="User who last modified the policy")
    
    # Statistics
    classifications_count: Optional[int] = Field(None, description="Number of classifications using this policy")
    
    model_config = {"from_attributes": True}

class PDCRetentionPolicyList(BaseModel):
    """Schema for paginated PDC Retention Policy list."""
    items: List[PDCRetentionPolicyResponse]
    total: int
    page: int
    size: int
    
    model_config = {"from_attributes": True}

class PDCRetentionPolicySummary(BaseModel):
    """Schema for retention policy summary statistics."""
    total_policies: int
    active_policies: int
    inactive_policies: int
    by_retention_type: dict
    by_jurisdiction: dict
    avg_retention_days: Optional[float]
    
    model_config = {"from_attributes": True}