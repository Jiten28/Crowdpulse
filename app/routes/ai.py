from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models.schemas import ChatRequest
from app.services.chat_service import answer_question
from app.services.data_store import data_store
from app.services.llm_client import LLMError
from app.services.rate_limiter import is_allowed
from app.services.reasoning_engine import generate_ops_brief

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _client_key(request: Request) -> str:
    """Per-client key for rate limiting, falling back to a constant if the client host is unavailable."""
    return request.client.host if request.client else "unknown"


@router.post("/ai/brief")
async def ai_brief(request: Request):
    if not is_allowed(f"brief:{_client_key(request)}", settings.RATE_LIMIT_CHAT_PER_MIN):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")

    flagged = data_store.get_flagged_statuses()
    if not flagged:
        return templates.TemplateResponse(
            "partials/ai_brief.html",
            {"request": request, "assessments": [], "error": None, "no_flags": True},
        )

    try:
        assessments = generate_ops_brief(flagged)
        return templates.TemplateResponse(
            "partials/ai_brief.html",
            {"request": request, "assessments": assessments, "error": None, "no_flags": False},
        )
    except LLMError as exc:
        return templates.TemplateResponse(
            "partials/ai_brief.html",
            {"request": request, "assessments": [], "error": str(exc), "no_flags": False},
        )


@router.post("/ai/chat")
async def ai_chat(request: Request, chat_request: ChatRequest):
    if not is_allowed(f"chat:{_client_key(request)}", settings.RATE_LIMIT_CHAT_PER_MIN):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")

    try:
        reply = answer_question(chat_request.message)
        return {"reply": reply}
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=f"AI assistant is temporarily unavailable: {exc}") from exc
