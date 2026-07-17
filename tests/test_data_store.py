from app.models.schemas import StatusLevel, ZoneReading
from app.services.data_store import DataStore


def make_reading(count, capacity, zone="Test Zone"):
    return ZoneReading(
        timestamp="2026-07-17T18:00:00Z",
        gate_id="A1",
        zone_name=zone,
        current_count=count,
        capacity=capacity,
        entry_rate=10.0,
    )


def test_normal_status_below_watch_threshold():
    store = DataStore()
    store.load([make_reading(3000, 10000)])  # 30%
    statuses = store.get_statuses()
    assert statuses[0].status == StatusLevel.NORMAL
    assert statuses[0].occupancy_pct == 30.0


def test_watch_status_at_threshold():
    store = DataStore()
    store.load([make_reading(7000, 10000)])  # exactly 70%
    statuses = store.get_statuses()
    assert statuses[0].status == StatusLevel.WATCH


def test_critical_status_above_threshold():
    store = DataStore()
    store.load([make_reading(9500, 10000)])  # 95%
    statuses = store.get_statuses()
    assert statuses[0].status == StatusLevel.CRITICAL


def test_statuses_sorted_by_occupancy_descending():
    store = DataStore()
    store.load([
        make_reading(1000, 10000, zone="Low"),
        make_reading(9000, 10000, zone="High"),
        make_reading(5000, 10000, zone="Mid"),
    ])
    statuses = store.get_statuses()
    assert [s.zone_name for s in statuses] == ["High", "Mid", "Low"]


def test_flagged_statuses_excludes_normal():
    store = DataStore()
    store.load([
        make_reading(1000, 10000, zone="Normal Zone"),
        make_reading(9500, 10000, zone="Critical Zone"),
    ])
    flagged = store.get_flagged_statuses()
    assert len(flagged) == 1
    assert flagged[0].zone_name == "Critical Zone"


def test_empty_store_reports_empty():
    store = DataStore()
    assert store.is_empty() is True
    store.load([make_reading(100, 1000)])
    assert store.is_empty() is False
