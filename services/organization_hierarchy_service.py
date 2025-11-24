from models.pdc_organization_hierarchy import PDCOrganizationHierarchy
from schemas.organization_hierarchy_schemas import PDCOrganizationHierarchyResponse
from sqlalchemy.orm import Session
from typing import List

class PDCOrganizationHierarchyService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[PDCOrganizationHierarchy]:
        return self.db.query(PDCOrganizationHierarchy).order_by(PDCOrganizationHierarchy.level).all()

    def get_all_api(self) -> List[dict]:
        orgs = self.get_all()
        return [PDCOrganizationHierarchyResponse.model_validate(org.to_dict()).model_dump() for org in orgs]
