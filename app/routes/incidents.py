from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.models.schemas import StatusLevel
from app.services.incident_log import export_csv, get_all_incidents, log_incident

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class LogIncidentRequest(BaseModel):
    """Body of a POST /incidents request."""

    zone_name: str = Field(min_length=1, max_length=100)
    action_taken: str = Field(min_length=1, max_length=300)
    status_at_time: StatusLevel


@router.post("/incidents")
async def create_incident(request: Request, body: LogIncidentRequest):
    """Logs an actioned recommendation and returns the refreshed incident log fragment."""
    try:
        log_incident(body.zone_name, body.action_taken, body.status_at_time)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not save incident.") from exc

    return templates.TemplateResponse(
        "partials/incident_log.html",
        {"request": request, "incidents": get_all_incidents()},
    )


@router.get("/incidents/export")
async def export_incidents():
    """Streams the full incident log back as a downloadable CSV."""
    csv_data = export_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=crowdpulse_incident_log.csv"},
    )
