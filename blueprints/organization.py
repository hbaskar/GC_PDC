import azure.functions as func
import json
import logging
from database.config import get_db
from services.organization_service import PDCOrganizationService

bp = func.Blueprint()

@bp.route(route="organization/stream-business-unit/{organization_id:int}", methods=["GET"])
def get_stream_and_business_unit(req: func.HttpRequest) -> func.HttpResponse:
    """Get stream and business unit names for a given organization id."""
    try:
        organization_id = int(req.route_params.get("organization_id"))
        db = next(get_db())
        service = PDCOrganizationService(db)
        result = service.get_stream_and_business_unit(organization_id)
        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error getting stream/business unit: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get stream/business unit", "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
