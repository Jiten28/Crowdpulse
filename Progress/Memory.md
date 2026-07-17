# Memory.md — CrowdPulse

**Purpose:** This file is the single source of truth for "what has actually been built so far." Any AI tool (Claude, ChatGPT, Cursor, etc.) picking up this project — in a new chat, or after switching models — must read this file FIRST, before PRD/Architecture/Rules/Phases, and before reading the codebase.

**Update rule:** update this file at the END of every work session or every completed phase, whichever comes first. Never leave it stale.

**Read order for a new AI session:** Memory.md (this file, inside the progress/ folder) → Phases.md → Rules.md → relevant parts of Architecture.md/PRD.md as needed.

---

## Current Status
- Full app built and locally verified across two test passes. LLM provider is now swappable (Gemini free tier or Anthropic paid). Favicon and logo mark added.
- Last updated: 2026-07-17
- Deployed URL: not yet filled in — user needs to deploy to Render
- GitHub repo: not yet pushed

## Completed Phases
- Phase 0 Scaffold: done, health check verified.
- Phase 1 Data Ingestion and Dashboard: done, CSV upload/parsing/status calc tested locally with real HTTP requests, confirmed correct.
- Phase 2 GenAI Reasoning Engine: done. Structured JSON validated, retry-then-graceful-failure verified against both providers with invalid/blocked credentials — confirmed it never crashes or fakes data.
- Phase 3 Ops Chat: done, context injection, sanitization, and rate limiting implemented and verified structurally (rate limiter confirmed to actually block after threshold).
- Phase 4 Incident Log and Export: done and verified locally — logging and CSV export both confirmed working end-to-end.
- Phase 5 Accessibility and Security: mostly done — ARIA labels, keyboard focus states, icon+text status badges, input validation, rate limiting, CORS scoping, no hardcoded secrets. Not verified in an actual screen reader.
- Branding: favicon (SVG, `/static/favicon.svg`) and a matching logo mark in the dashboard header added. Simple pulse-waveform icon in the existing color palette — no external assets, no copyright risk.

## In-Progress Phase
Phase 6 Tests and README and Polish: 18/18 tests passing in a clean isolated venv (not just the dev environment). README updated for the two-provider setup. Still needed from user: get a free Gemini API key, run the app with a real key, confirm AI Brief/Chat output quality, deploy to Render, fill in deployed link, push to GitHub, write LinkedIn post.

## Key Decisions Log
- 2026-07-17: Scoped to persona = Organizer, verticals = Crowd Management + Operational Intelligence/Real-Time Decision Support.
- 2026-07-17: Stack finalized as FastAPI + Jinja2/vanilla JS + Tailwind CDN, no frontend framework, no vector DB.
- 2026-07-17: **Switched default LLM provider from Anthropic to Gemini.** Reason: user's Anthropic account had no credits ("Your credit balance is too low" — confirmed via live error in their terminal), and Gemini has a genuine no-credit-card free tier (~1,500 req/day on Flash) suitable for a zero-budget hackathon submission. `llm_client.py` now dispatches to either provider via the `LLM_PROVIDER` env var; `reasoning_engine.py` and `chat_service.py` were NOT touched, confirming the original provider-agnostic design decision was correct. Anthropic path kept as a fallback for anyone with credits.

## Known Issues / Blockers (fixed during build — kept here so no one re-introduces them)
1. `anthropic` SDK was initially pinned to 0.34.2, incompatible with the httpx version it pulls in (crashed with `Client.__init__() got an unexpected keyword argument 'proxies'`). Fixed: pinned to `anthropic==0.69.0`.
2. Used a placeholder/incorrect model string `claude-sonnet-4-6` initially. Fixed: corrected to `claude-sonnet-5`.
3. Adding `google-genai==2.12.1` initially conflicted with the pinned `pydantic==2.9.2` (google-genai requires `pydantic>=2.12.5`). Fixed: bumped to `pydantic==2.13.4`. **Verified via a from-scratch isolated venv install with zero conflicts, not just an incremental install** — this is a stronger check than reusing an existing environment.

## Still Not Verified (be honest about this — don't assume it works until it's actually been seen working)
- Real AI-generated output quality/relevance from either provider has NOT been observed yet — all testing so far has deliberately used invalid/blocked keys to verify graceful failure. The user needs to add a real Gemini key and confirm the actual brief/chat content is good, not just that the plumbing doesn't crash.
- Screen reader accessibility (built to WCAG-aware markup conventions, but not tested with an actual screen reader)

## File Manifest
All files from the original scaffold exist and are wired up:
```
[x] app/main.py
[x] app/config.py — now supports LLM_PROVIDER switch
[x] app/models/schemas.py
[x] app/services/data_store.py
[x] app/services/csv_parser.py
[x] app/services/llm_client.py — now dual-provider (Gemini + Anthropic)
[x] app/services/reasoning_engine.py
[x] app/services/chat_service.py
[x] app/services/incident_log.py
[x] app/services/rate_limiter.py
[x] app/routes/upload.py
[x] app/routes/dashboard.py
[x] app/routes/ai.py
[x] app/routes/incidents.py
[x] app/templates/* — includes favicon + logo mark now
[x] app/static/app.js
[x] app/static/favicon.svg — new
[x] data/sample_gate_data.csv
[x] tests/* — 18/18 passing in clean venv
[x] README.md
[x] requirements.txt / .env.example / .gitignore / render.yaml / Procfile
```

## Next Action for Whoever Picks This Up
Get a free Gemini API key from https://aistudio.google.com/apikey, add it to `.env`, run the app, and actually read the AI Brief and Chat output for quality before deploying. Then deploy to Render and complete the remaining Phase 6 items above.

---
### Template for future entries (copy this block when updating)
```
## Update — [date]
**What changed:** ...
**What works (verified, not assumed):** ...
**What's incomplete/stubbed:** ...
**Deviations from Architecture/Rules/Design docs (and why):** ...
**Next action:** ...
```
