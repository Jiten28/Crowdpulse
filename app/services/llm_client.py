"""
Single point of contact with the GenAI provider. Every other service calls
generate()/generate_json() from here — nothing else in the app imports a
provider SDK directly. Which provider is used is controlled entirely by the
LLM_PROVIDER env var; reasoning_engine.py and chat_service.py never change
regardless of which one is active (this is the payoff of the
provider-agnostic design from Architecture.md §4).

Supported providers:
- "gemini"    — Google's Gemini API, has a genuine free tier (no credit card,
                no expiration as of mid-2026). Recommended default for this
                project so evaluators/testers aren't blocked by billing.
- "anthropic" — Claude via the Anthropic API. Paid — requires credits on the
                account. Higher quality reasoning, use if you have credits.
"""
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM call fails or returns unusable output."""
    pass


# ---------------------------------------------------------------------------
# Anthropic backend
# ---------------------------------------------------------------------------
_anthropic_client = None


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        if not settings.ANTHROPIC_API_KEY:
            raise LLMError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
        _anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


def _generate_anthropic(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    import anthropic
    try:
        client = _get_anthropic_client()
        response = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text_blocks = [block.text for block in response.content if block.type == "text"]
        if not text_blocks:
            raise LLMError("Anthropic returned no text content.")
        return "".join(text_blocks)
    except anthropic.APIError as exc:
        logger.error("Anthropic API error: %s", exc)
        raise LLMError(f"Anthropic API error: {exc}") from exc


# ---------------------------------------------------------------------------
# Gemini backend
# ---------------------------------------------------------------------------
_gemini_client = None


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        if not settings.GEMINI_API_KEY:
            raise LLMError("GEMINI_API_KEY is not set. Add it to your .env file.")
        _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _gemini_client


def _build_config(system_prompt: str, max_tokens: int, json_mode: bool, use_thinking_level: bool):
    from google.genai import types
    return types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if json_mode else "text/plain",
        # Gemini 3.x models (which gemini-flash-latest currently resolves to)
        # CANNOT fully disable thinking — thinking_budget=0 is silently
        # ignored on these models, unlike the older 2.5 series where it
        # actually turns thinking off. MINIMAL is the closest equivalent for
        # Gemini 3.x. Older/other models may reject thinking_level entirely,
        # so this is attempted first and the caller falls back to no
        # thinking_config at all if the API rejects the parameter.
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL") if use_thinking_level else None,
    )


def _generate_gemini(system_prompt: str, user_prompt: str, max_tokens: int, json_mode: bool) -> str:
    from google.genai import errors as genai_errors

    client = _get_gemini_client()

    # Generous headroom is the real safety net here, not the thinking
    # control — even MINIMAL thinking still consumes some tokens on Gemini
    # 3.x ("still requires thought signatures" per Google's docs), so we
    # can't assume thinking uses zero budget even when minimized.
    effective_max_tokens = max(max_tokens, 1500)

    for use_thinking_level in (True, False):
        try:
            config = _build_config(system_prompt, effective_max_tokens, json_mode, use_thinking_level)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=user_prompt,
                config=config,
            )
            if not response.text:
                raise LLMError("Gemini returned no text content.")
            return response.text
        except genai_errors.APIError as exc:
            # If thinking_level itself was rejected (e.g. an older model that
            # doesn't support it), retry once without any thinking_config
            # rather than failing the whole request over a param mismatch.
            if use_thinking_level and "thinking_level" in str(exc).lower():
                logger.warning("thinking_level not supported by this model, retrying without it.")
                continue
            logger.error("Gemini API error: %s", exc)
            raise LLMError(f"Gemini API error: {exc}") from exc

    raise LLMError("Gemini call failed after retrying without thinking_level.")


# ---------------------------------------------------------------------------
# Public interface — the only functions the rest of the app should call
# ---------------------------------------------------------------------------
def generate(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
    """
    Calls the configured provider with a system + user prompt, returns raw
    text. Raises LLMError on any failure — callers decide how to degrade
    gracefully.
    """
    try:
        if settings.LLM_PROVIDER == "gemini":
            return _generate_gemini(system_prompt, user_prompt, max_tokens, json_mode=False)
        elif settings.LLM_PROVIDER == "anthropic":
            return _generate_anthropic(system_prompt, user_prompt, max_tokens)
        else:
            raise LLMError(f"Unknown LLM_PROVIDER '{settings.LLM_PROVIDER}'. Use 'gemini' or 'anthropic'.")
    except LLMError:
        raise
    except Exception as exc:
        logger.error("Unexpected LLM error: %s", exc)
        raise LLMError(f"Unexpected error calling LLM: {exc}") from exc


def generate_json(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> dict | list:
    """
    Calls the configured provider and parses the result as JSON. For Gemini,
    JSON mode is requested natively via response_mime_type. For Anthropic
    (no native JSON mode), the system prompt must instruct the model to
    return ONLY JSON — this function strips common wrapping artifacts as a
    safety net either way.
    """
    try:
        if settings.LLM_PROVIDER == "gemini":
            raw = _generate_gemini(system_prompt, user_prompt, max_tokens, json_mode=True)
        elif settings.LLM_PROVIDER == "anthropic":
            raw = _generate_anthropic(system_prompt, user_prompt, max_tokens)
        else:
            raise LLMError(f"Unknown LLM_PROVIDER '{settings.LLM_PROVIDER}'. Use 'gemini' or 'anthropic'.")
    except LLMError:
        raise
    except Exception as exc:
        logger.error("Unexpected LLM error: %s", exc)
        raise LLMError(f"Unexpected error calling LLM: {exc}") from exc

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
