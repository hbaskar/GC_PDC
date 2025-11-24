from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PDCTemplateBase(BaseModel):
    template_name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=250)
    version: Optional[str] = Field(None, max_length=20)
    is_active: bool = True

class PDCTemplateCreate(PDCTemplateBase):
    created_by: str

class PDCTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=250)
    version: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    modified_by: Optional[str] = None

class PDCTemplateOut(PDCTemplateBase):
    template_id: int
    created_at: datetime
    created_by: str
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None

    class Config:
        orm_mode = True
