from models.pdc_template import PDCTemplate
from schemas.template_schemas import PDCTemplateCreate, PDCTemplateUpdate
from datetime import datetime

class TemplateService:
    def __init__(self, db):
        self.db = db

    def create(self, data: PDCTemplateCreate):
        template = PDCTemplate(
            template_name=data.template_name,
            description=data.description,
            version=data.version,
            is_active=data.is_active,
            created_at=datetime.utcnow(),
            created_by=data.created_by
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_by_id(self, template_id: int):
        return self.db.query(PDCTemplate).filter(PDCTemplate.template_id == template_id).first()

    def get_all(self):
        return self.db.query(PDCTemplate).all()

    def update(self, template_id: int, data: PDCTemplateUpdate):
        template = self.get_by_id(template_id)
        if not template:
            return None
        for field, value in data.dict(exclude_unset=True).items():
            setattr(template, field, value)
        template.modified_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template_id: int):
        template = self.get_by_id(template_id)
        if not template:
            return False
        self.db.delete(template)
        self.db.commit()
        return True
