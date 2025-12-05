from pydantic import BaseModel, Field
from typing import Optional

class PDCOrganizationHierarchyResponse(BaseModel):
    organization_id: int = Field(...)
    name: str = Field(...)
    code: str = Field(...)
    description: Optional[str] = Field(None)
    org_level: Optional[str] = Field(None)
    parent_organization_id: Optional[int] = Field(None)
    hierarchy_path: Optional[str] = Field(None)
    level: Optional[int] = Field(None)
    stream: Optional[str] = Field(None)
    business_unit: Optional[str] = Field(None)

    model_config = {"extra": "allow"}
