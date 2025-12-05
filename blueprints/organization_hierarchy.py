import azure.functions as func
import json
import logging
from database.config import get_db
from services.organization_hierarchy_service import PDCOrganizationHierarchyService
from schemas.organization_hierarchy_schemas import PDCOrganizationHierarchyResponse

bp = func.Blueprint()

@bp.route(route="organization-hierarchy", methods=["GET"])
def get_organization_hierarchy(req: func.HttpRequest) -> func.HttpResponse:
    """Get organization hierarchy records, optionally filtered by org_level (e.g., SubEntity)."""
    try:
        db = next(get_db())
        service = PDCOrganizationHierarchyService(db)
        org_level = req.params.get("org_level")
        if org_level:
            from models.pdc_organization_hierarchy import PDCOrganizationHierarchy
            from schemas.organization_hierarchy_schemas import PDCOrganizationHierarchyResponse
            items = service.db.query(PDCOrganizationHierarchy).filter(
                PDCOrganizationHierarchy.org_level == org_level
            ).order_by(PDCOrganizationHierarchy.level).all()
            items = [PDCOrganizationHierarchyResponse.model_validate(org.to_dict()).model_dump() for org in items]
        else:
            items = service.get_all_api()
        return func.HttpResponse(
            json.dumps({"items": items}, default=str),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error getting organization hierarchy: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get organization hierarchy", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
