
import logging
from models.pdc_organization import PDCOrganization
from sqlalchemy.orm import Session
from typing import Optional, Dict
from schemas.organization_schemas import PDCOrganizationSchema

class PDCOrganizationService:
    def __init__(self, db: Session):
        self.db = db

    def get_stream_name(self, organization_id: int) -> Optional[str]:
        org = self.db.query(PDCOrganization).filter(PDCOrganization.organization_id == organization_id).first()
        #logging.info({"organization_id": organization_id, "organization": org.to_dict() if org else None})
        if org and org.parent_organization_id:
            parent_org = self.db.query(PDCOrganization).filter(PDCOrganization.organization_id == org.parent_organization_id).first()
            return parent_org.name if parent_org else None
        else:
            return org.name if org else None

    def get_business_unit_name(self, organization_id: int) -> Optional[str]:

        org = self.db.query(PDCOrganization).filter(PDCOrganization.organization_id == organization_id).first()
        if org.parent_organization_id:
            
            return org.name if org else None
        else:
            return None

    def get_stream_and_business_unit(self, organization_id: int) -> Dict[str, Optional[str]]:
        return {
            "stream": self.get_stream_name(organization_id),
            "business_unit": self.get_business_unit_name(organization_id)
        }
