import pytest

from app.services.csv_parser import CSVValidationError, parse_csv_bytes

VALID_CSV = (
    b"timestamp,gate_id,zone_name,current_count,capacity,entry_rate\n"
    b"2026-07-17T18:00:00Z,A1,North Gate,3200,4000,45\n"
    b"2026-07-17T18:00:00Z,B1,South Gate,1000,4000,10\n"
)


def test_valid_csv_parses_correctly():
    """A well-formed CSV with all required columns parses into the expected ZoneReading objects."""
    readings = parse_csv_bytes(VALID_CSV, max_mb=2)
    assert len(readings) == 2
    assert readings[0].zone_name == "North Gate"
    assert readings[0].current_count == 3200


def test_empty_file_rejected():
    """A zero-byte upload is rejected with a clear message instead of crashing."""
    with pytest.raises(CSVValidationError, match="empty"):
        parse_csv_bytes(b"", max_mb=2)


def test_oversized_file_rejected():
    """A file exceeding the configured MB limit is rejected before being parsed."""
    # ~3MB of padding, exceeds a 2MB limit
    big = VALID_CSV + b"x" * (3 * 1024 * 1024)
    with pytest.raises(CSVValidationError, match="exceeds"):
        parse_csv_bytes(big, max_mb=2)


def test_missing_required_columns_rejected():
    """A CSV missing one or more required columns is rejected with the missing column names listed."""
    bad_csv = b"timestamp,gate_id,zone_name\n2026-07-17T18:00:00Z,A1,North Gate\n"
    with pytest.raises(CSVValidationError, match="missing required column"):
        parse_csv_bytes(bad_csv, max_mb=2)


def test_header_only_csv_rejected():
    """A CSV with headers but zero data rows is rejected as having no data."""
    header_only = b"timestamp,gate_id,zone_name,current_count,capacity,entry_rate\n"
    with pytest.raises(CSVValidationError, match="no data rows"):
        parse_csv_bytes(header_only, max_mb=2)


def test_non_csv_content_rejected():
    """Binary/garbage content that isn't valid CSV is rejected, not silently turned into empty results."""
    with pytest.raises(CSVValidationError):
        parse_csv_bytes(b"\x00\x01\x02 this is not a csv \xff\xfe", max_mb=2)


def test_partially_bad_rows_are_skipped_not_fatal():
    """One malformed row does not fail the whole upload — valid rows still parse successfully."""
    mixed = (
        b"timestamp,gate_id,zone_name,current_count,capacity,entry_rate\n"
        b"2026-07-17T18:00:00Z,A1,North Gate,3200,4000,45\n"
        b"2026-07-17T18:00:00Z,B1,Bad Row,not_a_number,4000,10\n"
    )
    readings = parse_csv_bytes(mixed, max_mb=2)
    # One good row should still come through even though the other is malformed
    assert len(readings) == 1
    assert readings[0].zone_name == "North Gate"
