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
        with get_db() as db:
            service = PDCOrganizationHierarchyService(db)
            org_level = req.params.get("org_level")
            if org_level:
                items = service.get_api_by_org_level(org_level)
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
