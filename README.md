# CrowdPulse — GenAI Crowd Command Center for Tournament Organizers

Built for **PromptWars Virtual — Challenge 4: Smart Stadiums & Tournament Operations**.

**Persona:** Tournament Organizer
**Verticals:** Crowd Management + Operational Intelligence / Real-Time Decision Support

## What this is

CrowdPulse gives a stadium operations organizer a live view of gate/zone crowd density and uses GenAI to **reason** over that data — not just display it. When zones cross a risk threshold, the app sends the actual numbers to an LLM, which assesses each one and returns a structured recommendation (risk level, reasoning, recommended action, urgency). Organizers can also ask free-form questions in an ops chat, grounded in whatever data is currently loaded.

## Why a CSV upload instead of a live feed

There's no real stadium IoT/turnstile feed available for this challenge. Per the challenge's own guidance, the app is built so an evaluator can test the full logic by uploading data manually. A realistic sample dataset ships in `data/sample_gate_data.csv` — upload it on the dashboard to see the app fully functional in under a minute, including a mix of Normal, Watch, and Critical zones so the AI reasoning has something real to work with.

## How the GenAI is actually used (not decorative)

- **AI Ops Brief** (`app/services/reasoning_engine.py`): sends real occupancy/entry-rate data for flagged zones to Claude with a structured system prompt, requiring a JSON response validated against a strict schema. If you remove the LLM call, this feature produces nothing — there's no hardcoded fallback logic pretending to be AI.
- **Ops Chat** (`app/services/chat_service.py`): injects the current dataset as context into every question, so answers are grounded in whatever is actually loaded, not generic chatbot responses.

## Setup

```bash
git clone https://github.com/Jiten28/Crowdpulse
cd crowdpulse
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`:

- **Recommended (free):** leave `LLM_PROVIDER=gemini` and get a free key at https://aistudio.google.com/apikey — no credit card, no expiration, ~1,500 requests/day on Gemini 2.5 Flash.
- **Alternative (paid):** set `LLM_PROVIDER=anthropic` and add a funded `ANTHROPIC_API_KEY` from console.anthropic.com if you'd rather use Claude and have credits available.

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000`.

## Deployment

Deployed on Render using `render.yaml` (or `Procfile` as a fallback). Set `LLM_PROVIDER` and the matching API key (`GEMINI_API_KEY` or `ANTHROPIC_API_KEY`) as environment variables in the Render dashboard — never commit them.

**Live deployed link: https://crowdpulse-70bq.onrender.com**

## How to test end-to-end (evaluator path)

1. Open the deployed link.
2. Upload `data/sample_gate_data.csv` (already in the repo) using the "Load" button.
3. Confirm the zone grid populates with a mix of Normal / Watch / Critical statuses.
4. Click **Generate AI Brief** — confirm real, data-specific reasoning and recommendations appear for the Watch/Critical zones (not generic text).
5. In the Ops Chat, ask: _"Which gates are critical right now?"_ and _"What should I do about the busiest zone?"_ — confirm answers reference the actual uploaded numbers.
6. Click **Mark as Actioned** on a recommendation — confirm it appears in the Incident Log below.
7. Click **Export CSV** — confirm a valid CSV downloads with the logged action.
8. Try uploading a non-CSV file or an empty file — confirm a clear error message, not a crash.

All 8 steps above have been manually verified working end-to-end against a live Gemini API key (not just localhost during development — see Memory.md for the full verification history, including issues found and fixed along the way).

## Running tests

```bash
pytest tests/ -v
```

18 tests covering CSV validation edge cases, occupancy/status calculation, and reasoning-engine JSON validation (LLM calls are mocked in tests — no live API calls during automated testing).

## Troubleshooting

**"This model models/... is no longer available" (404/403 from Gemini):** Google has been retiring specific Gemini model versions early for new API keys throughout 2026, sometimes ahead of their official deprecation date. The app uses `gemini-flash-latest`, Google's self-updating alias, specifically to avoid this — but if Google renames the alias itself, check the current model list at https://ai.google.dev/gemini-api/docs/models and update `GEMINI_MODEL` in `.env`.

**AI responses cut off mid-sentence:** Gemini 3.x models (which `gemini-flash-latest` currently resolves to) spend part of their output budget on internal "thinking" before writing the visible answer, and — unlike the older 2.5 series — this thinking cannot be fully disabled on 3.x models. The app already handles this: it requests `thinking_level="MINIMAL"` (the correct 3.x control) with a fallback if that's ever rejected, plus a hard minimum token floor on every call. If you still see truncation after changing models, increase `max_tokens` in `reasoning_engine.py` (AI Brief) or `chat_service.py` (Ops Chat).

**"Your credit balance is too low" (Anthropic):** you're on `LLM_PROVIDER=anthropic` without funded credits. Either add credits at console.anthropic.com, or switch to `LLM_PROVIDER=gemini` in `.env` (no cost).

## Security notes

- No API keys in code or version control (`.env` is git-ignored, `.env.example` ships with empty values)
- Uploaded files validated for type, size, and required columns before processing
- Chat input length-limited and sanitized before reaching the LLM prompt; system prompt explicitly instructs the model to ignore embedded instructions (basic prompt-injection defense)
- `/ai/chat` and `/ai/brief` are rate-limited per IP
- CORS restricted via `ALLOWED_ORIGIN` env var (set to your actual deployed origin in production, not `*`)

## Accessibility notes

- WCAG-aware color contrast on the dark theme
- Status is never conveyed by color alone (icon + text label on every status badge)
- All interactive elements keyboard-reachable with visible focus states
- Form inputs use real `<label>` elements, not placeholder-only labeling
- Chat log uses `aria-live` so new messages are announced

## Architecture

See `Architecture.md` for the full breakdown. Short version: FastAPI + Jinja2-rendered HTML + vanilla JS (no frontend framework, no build step), in-memory dataset + a single SQLite table for the incident log, single provider-agnostic LLM wrapper (`app/services/llm_client.py`).

## Explicitly out of scope

Fan-facing features, transportation, sustainability, multilingual UI, volunteer tools, and any vertical beyond Crowd Management + Operational Intelligence. See `PRD.md` §3 for the reasoning — this was a deliberate scoping decision, not an oversight.
