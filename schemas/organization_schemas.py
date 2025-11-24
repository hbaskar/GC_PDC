from pydantic import BaseModel
from typing import Optional

class PDCOrganizationSchema(BaseModel):
    organization_id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    org_level: Optional[str] = None
    parent_organization_id: Optional[int] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True
