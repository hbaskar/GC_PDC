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
        # Build a lookup for parent name resolution.
        id_to_name = {org.organization_id: org.name for org in orgs}

        enriched = []
        for org in orgs:
            base = org.to_dict()
            is_subentity = org.org_level and org.org_level.lower() == "subentity"
            stream = id_to_name.get(org.parent_organization_id) if is_subentity else None
            business_unit = org.name if is_subentity else None
            base["stream"] = stream
            base["business_unit"] = business_unit
            enriched.append(PDCOrganizationHierarchyResponse.model_validate(base).model_dump())

        return enriched

    def get_api_by_org_level(self, org_level: str) -> List[dict]:
        orgs = self.get_all()
        id_to_name = {org.organization_id: org.name for org in orgs}

        target_level = org_level.lower() if org_level else None
        enriched = []
        for org in orgs:
            if target_level and (org.org_level or "").lower() != target_level:
                continue
            base = org.to_dict()
            is_subentity = org.org_level and org.org_level.lower() == "subentity"
            stream = id_to_name.get(org.parent_organization_id) if is_subentity else None
            business_unit = org.name if is_subentity else None
            base["stream"] = stream
            base["business_unit"] = business_unit
            enriched.append(PDCOrganizationHierarchyResponse.model_validate(base).model_dump())

        return enriched
