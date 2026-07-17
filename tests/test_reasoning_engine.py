import pytest

from app.models.schemas import StatusLevel, ZoneStatus
from app.services.llm_client import LLMError
from app.services import reasoning_engine


def make_zone_status(name="Test Zone", status=StatusLevel.CRITICAL):
    return ZoneStatus(
        gate_id="A1",
        zone_name=name,
        current_count=3900,
        capacity=4000,
        occupancy_pct=97.5,
        entry_rate=50.0,
        status=status,
    )


def test_no_flagged_zones_returns_empty_without_calling_llm(mocker):
    spy = mocker.patch("app.services.reasoning_engine.generate_json")
    result = reasoning_engine.generate_ops_brief([])
    assert result == []
    spy.assert_not_called()


def test_valid_llm_response_parses_into_risk_assessments(mocker):
    mock_response = [
        {
            "zone_name": "Test Zone",
            "risk_level": "Critical",
            "reasoning": "Occupancy is at 97.5% and still climbing based on entry rate.",
            "recommended_action": "Redirect incoming fans to Gate B2 immediately.",
            "urgency": "high",
        }
    ]
    mocker.patch("app.services.reasoning_engine.generate_json", return_value=mock_response)

    result = reasoning_engine.generate_ops_brief([make_zone_status()])

    assert len(result) == 1
    assert result[0].zone_name == "Test Zone"
    assert result[0].risk_level == StatusLevel.CRITICAL
    assert result[0].urgency == "high"


def test_malformed_json_retries_then_raises(mocker):
    mock_gen = mocker.patch(
        "app.services.reasoning_engine.generate_json",
        side_effect=LLMError("not valid json"),
    )
    with pytest.raises(LLMError):
        reasoning_engine.generate_ops_brief([make_zone_status()])
    # One initial attempt + one retry = 2 calls, never more
    assert mock_gen.call_count == 2


def test_response_missing_required_field_is_rejected(mocker):
    bad_response = [{"zone_name": "Test Zone", "risk_level": "Critical"}]  # missing fields
    mocker.patch("app.services.reasoning_engine.generate_json", return_value=bad_response)
    with pytest.raises(LLMError):
        reasoning_engine.generate_ops_brief([make_zone_status()])


def test_invalid_urgency_value_is_rejected(mocker):
    bad_response = [
        {
            "zone_name": "Test Zone",
            "risk_level": "Critical",
            "reasoning": "Some valid reasoning text here.",
            "recommended_action": "Some valid action text here.",
            "urgency": "extremely-urgent",  # not one of low/medium/high
        }
    ]
    mocker.patch("app.services.reasoning_engine.generate_json", return_value=bad_response)
    with pytest.raises(LLMError):
        reasoning_engine.generate_ops_brief([make_zone_status()])
