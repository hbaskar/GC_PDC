"""
Pydantic schemas for PDC Lookup API.
Schemas for lookup types and lookup codes reference data.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# ========== LOOKUP TYPE SCHEMAS ==========

class PDCLookupTypeBase(BaseModel):
    """Base schema for PDC Lookup Type."""
    lookup_type: str = Field(..., min_length=1, max_length=50, description="Unique lookup type identifier")
    display_name: Optional[str] = Field(None, max_length=100, description="Human-readable display name")
    description: Optional[str] = Field(None, description="Description of the lookup type")
    is_active: bool = Field(True, description="Whether the lookup type is active")

class PDCLookupTypeCreate(PDCLookupTypeBase):
    """Schema for creating a new PDC Lookup Type."""
    created_by: str = Field(..., max_length=100, description="User who created the record")

class PDCLookupTypeUpdate(BaseModel):
    """Schema for updating a PDC Lookup Type."""
    display_name: Optional[str] = Field(None, max_length=100, description="Human-readable display name")
    description: Optional[str] = Field(None, description="Description of the lookup type")
    is_active: Optional[bool] = Field(None, description="Whether the lookup type is active")
    modified_by: Optional[str] = Field(None, max_length=100, description="User who modified the record")

class PDCLookupTypeResponse(PDCLookupTypeBase):
    """Schema for PDC Lookup Type response."""
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    
    model_config = {"from_attributes": True, "extra": "allow"}

# ========== LOOKUP CODE SCHEMAS ==========

class PDCLookupCodeBase(BaseModel):
    """Base schema for PDC Lookup Code."""
    lookup_type: str = Field(..., min_length=1, max_length=50, description="Parent lookup type")
    lookup_code: str = Field(..., min_length=1, max_length=50, description="Unique code within the type")
    display_name: Optional[str] = Field(None, max_length=100, description="Human-readable display name")
    description: Optional[str] = Field(None, description="Description of the lookup code")
    is_active: bool = Field(True, description="Whether the lookup code is active")
    sort_order: Optional[int] = Field(None, description="Display sort order")

class PDCLookupCodeCreate(PDCLookupCodeBase):
    """Schema for creating a new PDC Lookup Code."""
    created_by: str = Field(..., max_length=100, description="User who created the record")

class PDCLookupCodeUpdate(BaseModel):
    """Schema for updating a PDC Lookup Code."""
    display_name: Optional[str] = Field(None, max_length=100, description="Human-readable display name")
    description: Optional[str] = Field(None, description="Description of the lookup code")
    is_active: Optional[bool] = Field(None, description="Whether the lookup code is active")
    sort_order: Optional[int] = Field(None, description="Display sort order")
    modified_by: Optional[str] = Field(None, max_length=100, description="User who modified the record")

class PDCLookupCodeResponse(PDCLookupCodeBase):
    """Schema for PDC Lookup Code response."""
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    
    model_config = {"from_attributes": True, "extra": "allow"}

# ========== COMBINED RESPONSE SCHEMAS ==========

class PDCLookupTypeWithCodes(PDCLookupTypeResponse):
    """Schema for lookup type with its codes."""
    lookup_codes: List[PDCLookupCodeResponse] = Field(default_factory=list, description="Associated lookup codes")

class PDCLookupTypeList(BaseModel):
    """Schema for paginated lookup type list."""
    items: List[PDCLookupTypeResponse]
    total: int
    page: int
    size: int
    pages: int

class PDCLookupCodeList(BaseModel):
    """Schema for paginated lookup code list."""
    items: List[PDCLookupCodeResponse]
    total: int
    page: int
    size: int
    pages: int

# ========== SUMMARY SCHEMAS ==========

class PDCLookupTypeSummary(BaseModel):
    """Schema for simplified lookup type summary."""
    lookup_type: str
    display_name: Optional[str] = None
    is_active: bool = True
    code_count: Optional[int] = Field(None, description="Number of active codes in this type")
    
    model_config = {"from_attributes": True}

class PDCLookupCodeSummary(BaseModel):
    """Schema for simplified lookup code summary."""
    lookup_type: str
    lookup_code: str
    display_name: Optional[str] = None
    is_active: bool = True
    sort_order: Optional[int] = None
    
    model_config = {"from_attributes": True}
