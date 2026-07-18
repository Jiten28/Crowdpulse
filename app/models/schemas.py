"""
Pydantic models. These are the contracts between layers: csv_parser produces
ZoneReading, data_store computes ZoneStatus from it, reasoning_engine must
produce output matching RiskAssessment exactly (this is what we validate the
LLM's JSON against), and incident_log persists IncidentRecord.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class StatusLevel(str, Enum):
    NORMAL = "Normal"
    WATCH = "Watch"
    CRITICAL = "Critical"


class ZoneReading(BaseModel):
    """A single row from the uploaded CSV."""
    timestamp: str
    gate_id: str
    zone_name: str
    current_count: int = Field(ge=0)
    capacity: int = Field(gt=0)
    entry_rate: float = Field(ge=0, description="People entering per minute")

    @field_validator("current_count")
    @classmethod
    def count_not_absurd(cls, v: int) -> int:
        if v > 1_000_000:
            raise ValueError("current_count is unrealistically large")
        return v


class ZoneStatus(BaseModel):
    """ZoneReading + computed fields. What the dashboard renders."""
    gate_id: str
    zone_name: str
    current_count: int
    capacity: int
    occupancy_pct: float
    entry_rate: float
    status: StatusLevel


class RiskAssessment(BaseModel):
    """
    The exact JSON shape the LLM must return for each flagged zone.
    Validated on the way back from the model — if the LLM's output doesn't
    match this, the reasoning engine treats it as a failure and degrades
    gracefully rather than guessing.
    """
    zone_name: str
    risk_level: StatusLevel
    reasoning: str = Field(min_length=5, max_length=500)
    recommended_action: str = Field(min_length=5, max_length=300)
    urgency: str = Field(description="one of: low, medium, high")

    @field_validator("urgency")
    @classmethod
    def urgency_valid(cls, v: str) -> str:
        v_lower = v.lower().strip()
        if v_lower not in {"low", "medium", "high"}:
            raise ValueError("urgency must be low, medium, or high")
        return v_lower


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    reply: str


class IncidentRecord(BaseModel):
    id: Optional[int] = None
    timestamp: str
    zone_name: str
    action_taken: str
    status_at_time: StatusLevel
