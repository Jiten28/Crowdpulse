"""
Persists organizer-actioned recommendations to a single-table SQLite DB.
No ORM (see Rules.md §2) — the queries here are simple enough that raw
sqlite3 is clearer and lighter than adding SQLAlchemy as a dependency.
"""
import csv
import io
import sqlite3
from datetime import datetime, timezone
from typing import List

from app.config import settings
from app.models.schemas import IncidentRecord, StatusLevel


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.INCIDENT_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            zone_name TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            status_at_time TEXT NOT NULL
        )
        """
    )
    return conn


def log_incident(zone_name: str, action_taken: str, status_at_time: StatusLevel) -> IncidentRecord:
    timestamp = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    try:
        cursor = conn.execute(
            "INSERT INTO incidents (timestamp, zone_name, action_taken, status_at_time) VALUES (?, ?, ?, ?)",
            (timestamp, zone_name, action_taken, status_at_time.value),
        )
        conn.commit()
        return IncidentRecord(
            id=cursor.lastrowid,
            timestamp=timestamp,
            zone_name=zone_name,
            action_taken=action_taken,
            status_at_time=status_at_time,
        )
    finally:
        conn.close()


def get_all_incidents() -> List[IncidentRecord]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT id, timestamp, zone_name, action_taken, status_at_time FROM incidents ORDER BY id DESC"
        ).fetchall()
        return [
            IncidentRecord(id=r[0], timestamp=r[1], zone_name=r[2], action_taken=r[3], status_at_time=r[4])
            for r in rows
        ]
    finally:
        conn.close()


def export_csv() -> str:
    """Returns incident log as a CSV string, ready to be streamed as a download."""
    incidents = get_all_incidents()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "timestamp", "zone_name", "action_taken", "status_at_time"])
    for inc in incidents:
        writer.writerow([inc.id, inc.timestamp, inc.zone_name, inc.action_taken, inc.status_at_time.value])
    return buffer.getvalue()
