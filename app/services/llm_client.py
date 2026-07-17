"""
Single point of contact with the GenAI provider. Every other service calls
generate() from here — nothing else in the app imports the anthropic SDK
directly. If the provider ever needs to change, this is the only file that
changes (see Architecture.md §4).
"""
import json
import logging
from typing import Optional

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM call fails or returns unusable output."""
    pass


_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise LLMError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def generate(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
    """
    Calls the LLM with a system + user prompt, returns raw text response.
    Raises LLMError on any failure — callers decide how to degrade gracefully.
    """
    try:
        client = _get_client()
        response = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text_blocks = [block.text for block in response.content if block.type == "text"]
        if not text_blocks:
            raise LLMError("LLM returned no text content.")
        return "".join(text_blocks)
    except anthropic.APIError as exc:
        logger.error("Anthropic API error: %s", exc)
        raise LLMError(f"LLM API error: {exc}") from exc
    except Exception as exc:
        logger.error("Unexpected LLM error: %s", exc)
        raise LLMError(f"Unexpected error calling LLM: {exc}") from exc


def generate_json(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> dict | list:
    """
    Calls generate() and parses the result as JSON. The system prompt passed
    in must instruct the model to return ONLY JSON, no prose, no markdown
    fences — this function strips common wrapping artifacts as a safety net
    but the prompt should already avoid causing them.
    """
    raw = generate(system_prompt, user_prompt, max_tokens=max_tokens)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMError(f"LLM did not return valid JSON: {exc}. Raw output: {raw[:200]}") from exc
