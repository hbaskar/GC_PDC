import azure.functions as func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.pdc_template import PDCTemplate
from schemas.template_schemas import PDCTemplateCreate, PDCTemplateUpdate, PDCTemplateOut
from services.template_service import TemplateService
from database import get_db

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=PDCTemplateOut)
def create_template(data: PDCTemplateCreate, db: Session = Depends(get_db)):
    service = TemplateService(db)
    template = service.create(data)
    return template

@router.get("/{template_id}", response_model=PDCTemplateOut)
def get_template(template_id: int, db: Session = Depends(get_db)):
    service = TemplateService(db)
    template = service.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/", response_model=list[PDCTemplateOut])
def list_templates(db: Session = Depends(get_db)):
    service = TemplateService(db)
    return service.get_all()

@router.put("/{template_id}", response_model=PDCTemplateOut)
def update_template(template_id: int, data: PDCTemplateUpdate, db: Session = Depends(get_db)):
    service = TemplateService(db)
    template = service.update(template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}", response_model=dict)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    service = TemplateService(db)
    success = service.delete(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"success": True}
