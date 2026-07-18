"""
Central configuration. All environment-dependent values are loaded here and
nowhere else — routes and services should import from this module, never
call os.getenv() directly. This keeps secrets out of business logic and
makes it obvious where to look if a config value is wrong.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")

    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "2"))
    RATE_LIMIT_CHAT_PER_MIN: int = int(os.getenv("RATE_LIMIT_CHAT_PER_MIN", "10"))
    ALLOWED_ORIGIN: str = os.getenv("ALLOWED_ORIGIN", "*")
    INCIDENT_DB_PATH: str = os.getenv("INCIDENT_DB_PATH", "incidents.db")

    # Status thresholds (occupancy % of capacity)
    WATCH_THRESHOLD: float = 70.0
    CRITICAL_THRESHOLD: float = 90.0


settings = Settings()
