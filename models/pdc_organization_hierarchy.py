from sqlalchemy import Column, Integer, String
from .base import Base

class PDCOrganizationHierarchy(Base):
    __tablename__ = "pdc_org_hierarchy"

    organization_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(String(250))
    org_level = Column(String(50))
    parent_organization_id = Column(Integer)
    hierarchy_path = Column(String(250))
    level = Column(Integer)

    def to_dict(self):
        return {
            "organization_id": self.organization_id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "org_level": self.org_level,
            "parent_organization_id": self.parent_organization_id,
            "hierarchy_path": self.hierarchy_path,
            "level": self.level,
        }
