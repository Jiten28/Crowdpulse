"""
Holds the current uploaded dataset in memory (single-organizer, single-session
tool — no multi-tenant DB needed per Architecture.md). Computes occupancy %
and status level deterministically; these computed values are what get fed
into the GenAI reasoning prompt, so the LLM reasons over accurate numbers
rather than raw counts alone.
"""
from datetime import datetime, timezone
from typing import List, Optional

from app.config import settings
from app.models.schemas import StatusLevel, ZoneReading, ZoneStatus


def _status_for(occupancy_pct: float) -> StatusLevel:
    if occupancy_pct >= settings.CRITICAL_THRESHOLD:
        return StatusLevel.CRITICAL
    if occupancy_pct >= settings.WATCH_THRESHOLD:
        return StatusLevel.WATCH
    return StatusLevel.NORMAL


class DataStore:
    """Simple in-memory singleton-style store. One dataset at a time by design."""

    def __init__(self) -> None:
        self._readings: List[ZoneReading] = []
        self._uploaded_at: Optional[str] = None

    def load(self, readings: List[ZoneReading]) -> None:
        self._readings = readings
        self._uploaded_at = datetime.now(timezone.utc).isoformat()

    def is_empty(self) -> bool:
        return len(self._readings) == 0

    def uploaded_at(self) -> Optional[str]:
        return self._uploaded_at

    def get_statuses(self) -> List[ZoneStatus]:
        statuses = []
        for r in self._readings:
            occupancy_pct = round((r.current_count / r.capacity) * 100, 1) if r.capacity else 0.0
            statuses.append(
                ZoneStatus(
                    gate_id=r.gate_id,
                    zone_name=r.zone_name,
                    current_count=r.current_count,
                    capacity=r.capacity,
                    occupancy_pct=occupancy_pct,
                    entry_rate=r.entry_rate,
                    status=_status_for(occupancy_pct),
                )
            )
        # Highest risk first — most useful ordering for an organizer scanning quickly
        statuses.sort(key=lambda s: s.occupancy_pct, reverse=True)
        return statuses

    def get_flagged_statuses(self) -> List[ZoneStatus]:
        """Zones at Watch or Critical — these are what get sent to the LLM for reasoning."""
        return [s for s in self.get_statuses() if s.status != StatusLevel.NORMAL]

    def summary_text(self) -> str:
        """Compact text summary of current state, used as chat context."""
        statuses = self.get_statuses()
        if not statuses:
            return "No data currently loaded."
        lines = [
            f"{s.zone_name} (Gate {s.gate_id}): {s.current_count}/{s.capacity} "
            f"({s.occupancy_pct}% occupancy, entry rate {s.entry_rate}/min, status {s.status.value})"
            for s in statuses
        ]
        return f"Data as of {self._uploaded_at}:\n" + "\n".join(lines)


# Module-level singleton — fine for this single-organizer tool (see Architecture.md).
data_store = DataStore()
