from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.csv_parser import CSVValidationError, parse_csv_bytes
from app.services.data_store import data_store

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/upload")
async def upload_csv(request: Request, file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    raw = await file.read()
    try:
        readings = parse_csv_bytes(raw, max_mb=settings.MAX_UPLOAD_MB)
    except CSVValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    data_store.load(readings)

    # Return the refreshed zone grid + status bar as an HTML fragment so the
    # frontend can swap it in without a full page reload.
    return templates.TemplateResponse(
        "partials/zone_grid.html",
        {
            "request": request,
            "zones": data_store.get_statuses(),
            "uploaded_at": data_store.uploaded_at(),
        },
    )
