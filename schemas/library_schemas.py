"""
Pydantic schemas for PDC Library API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PDCLibraryBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Unique library code")
    name: str = Field(..., max_length=100, description="Library name")
    description: Optional[str] = Field(None, max_length=255, description="Library description")

class PDCLibraryCreate(PDCLibraryBase):
    pass

class PDCLibraryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Library name")
    description: Optional[str] = Field(None, max_length=255, description="Library description")

class PDCLibraryResponse(BaseModel):
    library_id: int = Field(..., description="Primary key")
    code: str = Field(..., description="Unique library code")
    name: str = Field(..., description="Library name")
    description: Optional[str] = Field(None, description="Library description")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    modified_at: Optional[datetime] = Field(None, description="Last modification timestamp")

    model_config = {"extra": "allow"}
