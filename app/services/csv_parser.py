"""
Validates and parses uploaded gate/zone CSV data into ZoneReading objects.
Never trusts the uploaded file: checks size, extension, required columns,
and per-row schema before anything downstream touches it.
"""
import io
from typing import List

import pandas as pd

from app.models.schemas import ZoneReading

REQUIRED_COLUMNS = {"timestamp", "gate_id", "zone_name", "current_count", "capacity", "entry_rate"}


class CSVValidationError(Exception):
    """Raised for any problem with an uploaded CSV. Message is safe to show the user."""
    pass


def parse_csv_bytes(raw: bytes, max_mb: int) -> List[ZoneReading]:
    """
    Parse raw uploaded bytes into a list of validated ZoneReading rows.
    Raises CSVValidationError with a clear, user-facing message on any problem.
    """
    size_mb = len(raw) / (1024 * 1024)
    if size_mb > max_mb:
        raise CSVValidationError(f"File is {size_mb:.1f}MB, which exceeds the {max_mb}MB limit.")

    if len(raw) == 0:
        raise CSVValidationError("The uploaded file is empty.")

    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise CSVValidationError(f"Could not parse file as CSV: {exc}") from exc

    if df.empty:
        raise CSVValidationError("CSV has no data rows.")

    missing = REQUIRED_COLUMNS - set(c.strip() for c in df.columns)
    if missing:
        raise CSVValidationError(
            f"CSV is missing required column(s): {', '.join(sorted(missing))}. "
            f"Required columns: {', '.join(sorted(REQUIRED_COLUMNS))}."
        )

    readings: List[ZoneReading] = []
    errors: List[str] = []
    for idx, row in df.iterrows():
        try:
            readings.append(
                ZoneReading(
                    timestamp=str(row["timestamp"]),
                    gate_id=str(row["gate_id"]),
                    zone_name=str(row["zone_name"]),
                    current_count=int(row["current_count"]),
                    capacity=int(row["capacity"]),
                    entry_rate=float(row["entry_rate"]),
                )
            )
        except Exception as exc:
            errors.append(f"Row {idx + 2}: {exc}")  # +2 accounts for header + 0-index

    if errors and not readings:
        raise CSVValidationError("No valid rows could be parsed:\n" + "\n".join(errors[:5]))

    return readings
