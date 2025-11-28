
import azure.functions as func
import json
from models.pdc_template import PDCTemplate
from schemas.template_schemas import PDCTemplateCreate, PDCTemplateUpdate, PDCTemplateOut
from services.template_service import TemplateService
from database import get_db

bp = func.Blueprint()

@bp.route(route="templates", methods=["POST"])
def create_template(req: func.HttpRequest) -> func.HttpResponse:
    db = next(get_db())
    data = req.get_json()
    service = TemplateService(db)
    template = service.create(PDCTemplateCreate(**data))
    return func.HttpResponse(json.dumps(template.to_dict()), mimetype="application/json", status_code=201)

@bp.route(route="templates/{template_id}", methods=["GET"])
def get_template(req: func.HttpRequest) -> func.HttpResponse:
    db = next(get_db())
    template_id = int(req.route_params["template_id"])
    service = TemplateService(db)
    template = service.get_by_id(template_id)
    if not template:
        return func.HttpResponse(json.dumps({"detail": "Template not found"}), mimetype="application/json", status_code=404)
    return func.HttpResponse(json.dumps(template.to_dict()), mimetype="application/json")

@bp.route(route="templates", methods=["GET"])
def list_templates(req: func.HttpRequest) -> func.HttpResponse:
    db = next(get_db())
    service = TemplateService(db)
    templates = service.get_all()
    return func.HttpResponse(json.dumps([t.to_dict() for t in templates]), mimetype="application/json")

@bp.route(route="templates/{template_id}", methods=["PUT"])
def update_template(req: func.HttpRequest) -> func.HttpResponse:
    db = next(get_db())
    template_id = int(req.route_params["template_id"])
    data = req.get_json()
    service = TemplateService(db)
    template = service.update(template_id, PDCTemplateUpdate(**data))
    if not template:
        return func.HttpResponse(json.dumps({"detail": "Template not found"}), mimetype="application/json", status_code=404)
    return func.HttpResponse(json.dumps(template.to_dict()), mimetype="application/json")

@bp.route(route="templates/{template_id}", methods=["DELETE"])
def delete_template(req: func.HttpRequest) -> func.HttpResponse:
    db = next(get_db())
    template_id = int(req.route_params["template_id"])
    service = TemplateService(db)
    success = service.delete(template_id)
    if not success:
        return func.HttpResponse(json.dumps({"detail": "Template not found"}), mimetype="application/json", status_code=404)
    return func.HttpResponse(json.dumps({"success": True}), mimetype="application/json")
