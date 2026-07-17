import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import ai, dashboard, incidents, upload

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CrowdPulse", description="GenAI Crowd Command Center for Tournament Organizers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard.router)
app.include_router(upload.router)
app.include_router(ai.router)
app.include_router(incidents.router)
