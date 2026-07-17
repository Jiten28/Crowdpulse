"""
The core GenAI feature (see Rules.md §8: this is the part that must NOT be
fakeable by removing the LLM call). Sends real, current zone data to the
model and asks it to reason about risk and recommend actions. Validates the
response against RiskAssessment; on failure, retries once with a stricter
instruction, then raises so the route can show a clearly-labeled
"unavailable" state rather than fabricating a result.
"""
import logging
from typing import List

from pydantic import ValidationError

from app.models.schemas import RiskAssessment, ZoneStatus
from app.services.llm_client import LLMError, generate_json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an operations intelligence assistant embedded in a stadium \
control room dashboard during a major tournament. You receive real-time crowd \
density data for gates/zones currently at Watch or Critical occupancy levels. \

For EACH zone provided, assess it and return your assessment. Consider: how far \
over the safe threshold it is, its entry rate (is it still filling up or stabilizing), \
and what a control-room organizer could realistically do in the next few minutes.

Respond with ONLY a JSON array, no prose, no markdown code fences. Each element must \
have exactly these fields:
- "zone_name": string, must match the zone_name given in the input exactly
- "risk_level": one of "Watch" or "Critical" (match or escalate the input status based on your judgment, never de-escalate below what the data shows)
- "reasoning": 1-2 sentences explaining WHY this zone is risky, referencing the actual numbers given
- "recommended_action": a specific, actionable instruction an organizer could act on immediately (e.g. redirect flow, open an additional gate, dispatch staff) — not a vague platitude
- "urgency": one of "low", "medium", "high"

Do not invent zones that weren't given to you. Do not omit any zone that was given to you."""


def _build_user_prompt(zones: List[ZoneStatus]) -> str:
    lines = []
    for z in zones:
        lines.append(
            f"- zone_name: {z.zone_name}, gate: {z.gate_id}, "
            f"occupancy: {z.current_count}/{z.capacity} ({z.occupancy_pct}%), "
            f"entry_rate: {z.entry_rate}/min, current_status: {z.status.value}"
        )
    return "Current flagged zones:\n" + "\n".join(lines)


def generate_ops_brief(flagged_zones: List[ZoneStatus]) -> List[RiskAssessment]:
    """
    Returns a validated list of RiskAssessment for the given flagged zones.
    Raises LLMError if the model can't be reached or its output can't be
    validated even after one retry — caller must handle this and show a
    graceful failure state, never a silent fallback.
    """
    if not flagged_zones:
        return []

    user_prompt = _build_user_prompt(flagged_zones)

    for attempt in (1, 2):
        try:
            prompt = user_prompt
            if attempt == 2:
                prompt += (
                    "\n\nIMPORTANT: your previous response was not valid JSON matching the "
                    "required schema. Return ONLY a raw JSON array, nothing else — no markdown "
                    "fences, no explanation text before or after."
                )
            raw = generate_json(SYSTEM_PROMPT, prompt, max_tokens=3000)
            if not isinstance(raw, list):
                raise ValueError("Expected a JSON array from the LLM.")

            assessments = [RiskAssessment(**item) for item in raw]
            logger.info("Ops brief generated successfully for %d zones.", len(assessments))
            return assessments

        except (LLMError, ValidationError, ValueError, TypeError) as exc:
            logger.warning("Ops brief attempt %d failed: %s", attempt, exc)
            if attempt == 2:
                raise LLMError(f"Could not generate a valid AI ops brief after retry: {exc}") from exc

    return []  # unreachable, satisfies type checkers
