from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.data_store import data_store
from app.services.incident_log import get_all_incidents

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "zones": data_store.get_statuses(),
            "uploaded_at": data_store.uploaded_at(),
            "is_empty": data_store.is_empty(),
            "incidents": get_all_incidents(),
            # Defaults for the included ai_brief.html partial on first page
            # load, before the organizer has clicked "Generate AI Brief".
            "assessments": [],
            "error": None,
            "no_flags": False,
        },
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
