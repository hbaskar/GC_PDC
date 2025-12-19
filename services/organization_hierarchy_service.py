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
        id_to_name = {org.organization_id: org.name for org in orgs}
        id_to_parent = {org.organization_id: org.parent_organization_id for org in orgs}

        enriched = []
        for org in orgs:
            base = org.to_dict()
            stream, business_unit = self._compute_stream_and_bu(org, id_to_name, id_to_parent)
            base["stream"] = stream
            base["business_unit"] = business_unit
            enriched.append(PDCOrganizationHierarchyResponse.model_validate(base).model_dump())

        return enriched

    def get_api_by_org_level(self, org_level: str) -> List[dict]:
        orgs = self.get_all()
        id_to_name = {org.organization_id: org.name for org in orgs}
        id_to_parent = {org.organization_id: org.parent_organization_id for org in orgs}

        target_level = org_level.lower() if org_level else None
        enriched = []
        for org in orgs:
            if target_level and (org.org_level or "").lower() != target_level:
                continue
            base = org.to_dict()
            stream, business_unit = self._compute_stream_and_bu(org, id_to_name, id_to_parent)
            base["stream"] = stream
            base["business_unit"] = business_unit
            enriched.append(PDCOrganizationHierarchyResponse.model_validate(base).model_dump())

        return enriched

    @staticmethod
    def _compute_stream_and_bu(org, id_to_name: dict, id_to_parent: dict):
        level = (org.org_level or "").lower()

        if level == "subentity":
            stream = id_to_name.get(org.parent_organization_id)
            business_unit = org.name
            return stream, business_unit

        if level == "entirty":
            # Special case: stream is the org's own name; business_unit is None.
            stream = org.name
            business_unit = None
            return stream, business_unit

        if level == "entity":
            # Entity: stream is the org's own name; business_unit remains None.
            stream = org.name
            business_unit = None
            return stream, business_unit

        if level == "enterprise":
            # Enterprise: business_unit = parent name, stream = grandparent name (if present).
            parent_id = org.parent_organization_id
            business_unit = id_to_name.get(parent_id)
            grandparent_id = id_to_parent.get(parent_id)
            stream = id_to_name.get(grandparent_id) if grandparent_id else None
            return stream, business_unit

        return None, None
