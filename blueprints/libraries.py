"""
PDC Libraries API Blueprint
CRUD endpoints for managing libraries.
"""
import azure.functions as func
from database.config import get_db
from models.pdc_library import PDCLibrary
from services.library_service import PDCLibraryService
from schemas.library_schemas import PDCLibraryResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
import json

bp = func.Blueprint()

@bp.route(route="libraries", methods=["GET"])
def get_libraries(req: func.HttpRequest) -> func.HttpResponse:
    with get_db() as db:
        service = PDCLibraryService(db)
        libraries = service.get_all()
        response = [PDCLibraryResponse.model_validate(lib.to_dict()).model_dump() for lib in libraries]
        return func.HttpResponse(json.dumps(response, default=str), mimetype="application/json")

@bp.route(route="libraries/{library_id:int}", methods=["GET"])
def get_library_by_id(req: func.HttpRequest) -> func.HttpResponse:
    library_id = int(req.route_params.get('library_id'))
    with get_db() as db:
        service = PDCLibraryService(db)
        library = service.get_by_id(library_id)
        if not library:
            return func.HttpResponse(json.dumps({"error": "Library not found"}), status_code=404, mimetype="application/json")
        response = PDCLibraryResponse.model_validate(library.to_dict()).model_dump()
        return func.HttpResponse(json.dumps(response, default=str), mimetype="application/json")

@bp.route(route="libraries", methods=["POST"])
def create_library(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "Invalid JSON"}), status_code=400, mimetype="application/json")
    code = req_body.get('code')
    name = req_body.get('name')
    description = req_body.get('description')
    library_group_id = req_body.get('library_group_id')
    created_by = req_body.get('created_by')
    with get_db() as db:
        service = PDCLibraryService(db)
        try:
            library = service.create(code=code, name=name, description=description, library_group_id=library_group_id, created_by=created_by)
            response = PDCLibraryResponse.model_validate(library.to_dict()).model_dump()
            return func.HttpResponse(json.dumps(response, default=str), status_code=201, mimetype="application/json")
        except IntegrityError as e:
            db.rollback()
            msg = "Library code already exists" if "duplicate" in str(e).lower() or "unique" in str(e).lower() else "Integrity error"
            detail = str(e)
            return func.HttpResponse(json.dumps({"error": msg, "detail": detail}), status_code=400, mimetype="application/json")

@bp.route(route="libraries/{library_id:int}", methods=["PUT"])
def update_library(req: func.HttpRequest) -> func.HttpResponse:
    library_id = int(req.route_params.get('library_id'))
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "Invalid JSON"}), status_code=400, mimetype="application/json")
    code = req_body.get('code')
    name = req_body.get('name')
    description = req_body.get('description')
    library_group_id = req_body.get('library_group_id')
    modified_by = req_body.get('modified_by')
    with get_db() as db:
        service = PDCLibraryService(db)
        library = service.update(library_id, code=code, name=name, description=description, library_group_id=library_group_id, modified_by=modified_by)
        if not library:
            return func.HttpResponse(json.dumps({"error": "Library not found"}), status_code=404, mimetype="application/json")
        response = PDCLibraryResponse.model_validate(library.to_dict()).model_dump()
        return func.HttpResponse(json.dumps(response, default=str), mimetype="application/json")

@bp.route(route="libraries/{library_id:int}", methods=["DELETE"])
def delete_library(req: func.HttpRequest) -> func.HttpResponse:
    library_id = int(req.route_params.get('library_id'))
    with get_db() as db:
        service = PDCLibraryService(db)
        success = service.delete(library_id)
        if not success:
            return func.HttpResponse(json.dumps({"error": "Library not found"}), status_code=404, mimetype="application/json")
        return func.HttpResponse(json.dumps({"success": True}), mimetype="application/json")
