# Memory.md — CrowdPulse

**Purpose:** This file is the single source of truth for "what has actually been built so far." Any AI tool (Claude, ChatGPT, Cursor, etc.) picking up this project — in a new chat, or after switching models — must read this file FIRST, before PRD/Architecture/Rules/Phases, and before reading the codebase.

**Update rule:** update this file at the END of every work session or every completed phase, whichever comes first. Never leave it stale.

**Read order for a new AI session:** Memory.md (this file, inside the progress/ folder) → Phases.md → Rules.md → relevant parts of Architecture.md/PRD.md as needed.

---

## Current Status
- **PROJECT IS FUNCTIONALLY COMPLETE AND VERIFIED.** Every core feature has been confirmed working end-to-end by the user against a real, live Gemini API key: CSV upload, dashboard status calculation, AI Ops Brief (specific, data-grounded, non-generic), Ops Chat (complete, accurate, correctly grounded answers, correctly declines off-topic requests), incident logging, and CSV export. Three real bugs were found through live testing and fixed (see Known Issues below) — none remain outstanding as of this update.
- Last updated: 2026-07-17 (session 5 — final verification)
- Remaining before submission: deploy to Render, verify on the deployed link (not just localhost), write LinkedIn post.
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

## Key Decisions Log (continued)
- 2026-07-17 (session 3): User ran the app live with a real Gemini API key. Upload, dashboard, incident log, and UI (including new favicon/logo) all confirmed working. AI Brief failed with `404 This model models/gemini-2.5-flash is no longer available to new users`. Investigated via web search: Google has been retiring specific Gemini model versions early for new API keys throughout 2026 (confirmed via multiple Google AI Developer Forum threads from the same week), ahead of official deprecation dates. **Fixed by switching `GEMINI_MODEL` from the hard-pinned `gemini-2.5-flash` to `gemini-flash-latest`, Google's self-updating alias** — this is Google's own recommended way to avoid exactly this class of breakage. Documented the fix and a troubleshooting section in README.md in case the alias itself ever gets renamed.

## Known Issues / Blockers (fixed during build — kept here so no one re-introduces them)
1. `anthropic` SDK was initially pinned to 0.34.2, incompatible with the httpx version it pulls in (crashed with `Client.__init__() got an unexpected keyword argument 'proxies'`). Fixed: pinned to `anthropic==0.69.0`.
2. Used a placeholder/incorrect model string `claude-sonnet-4-6` initially. Fixed: corrected to `claude-sonnet-5`.
3. Adding `google-genai==2.12.1` initially conflicted with the pinned `pydantic==2.9.2` (google-genai requires `pydantic>=2.12.5`). Fixed: bumped to `pydantic==2.13.4`. **Verified via a from-scratch isolated venv install with zero conflicts, not just an incremental install** — this is a stronger check than reusing an existing environment.
4. Chat responses were truncating mid-sentence for real data questions even after the thinking-budget fix, because max_tokens=400 was too tight for multi-zone answers. Fixed: raised to 1000 in chat_service.py. (Same underlying lesson as the ops-brief truncation: err generous on max_tokens for structured/multi-item answers, thinking_budget=0 alone isn't sufficient headroom.)
6. `thinking_budget=0` does not work on Gemini 3.x models at all (silently ignored, not an error) — this only works on the older Gemini 2.5 series. Spent two fix attempts on this before finding the real cause via research. Fixed: use `thinking_level="MINIMAL"` for 3.x, with automatic fallback to no thinking_config if that param is ever rejected, plus a hard 1500-token floor on every Gemini call as a backstop.
7. `GEMINI_MODEL` was hard-pinned to `gemini-2.5-flash`, which Google started blocking for new API keys (404 "no longer available to new users") — confirmed as an active, ongoing rollout via July 2026 Google AI Developer Forum threads, not a one-off fluke. Fixed: switched to `gemini-flash-latest`, Google's self-updating model alias, and added a README troubleshooting entry for this exact error class since Google may repeat this pattern.

## Verified Working (session 4 — user confirmed live, with real output observed)
- **AI Ops Brief: CONFIRMED WORKING with good output quality.** User ran it live against gemini-flash-latest and got specific, data-grounded reasoning for all 6 flagged zones (4 Critical, 2 Watch) with realistic urgency estimates and actionable, zone-specific recommendations (e.g. redirecting Gate C1 overflow to Gate C2 by name). This is real evidence the reasoning is grounded in the actual uploaded numbers, not templated.
- Root cause of the two prior AI Brief failures, both now fixed:
  1. `gemini-2.5-flash` blocked for new API keys → switched to `gemini-flash-latest` alias
  2. Output truncating mid-JSON → Gemini's internal "thinking" tokens were eating the output budget; fixed with `thinking_config=types.ThinkingConfig(thinking_budget=0)` in `llm_client.py`, and raised `max_tokens` from 1200 to 2500 in `reasoning_engine.py` for headroom with up to 6 flagged zones.

## Still Not Verified
- **Ops Chat**: CONFIRMED FULLY WORKING after 3 fix attempts (see Known Issues #6 for the full debugging history). User's final live test: "which gates are critical" and "what should I do about South Gate Plaza" both returned complete, specific, correctly-grounded multi-sentence answers referencing exact occupancy numbers and named alternate gates. "write me a poem" correctly declined and redirected to stadium-ops topics. No truncation. This is the `thinking_level="MINIMAL"` fix — confirmed working, not just theorized.
- **Incident logging + CSV export**: was verified working in an earlier session with dummy/no AI data present, but not re-tested since these code changes. Should be unaffected (this path doesn't touch the LLM at all) but worth a quick re-check.
- **Deployed (Render) version**: everything so far has been tested on localhost only. Deploying can surface new issues (missing env vars, static file path differences) that don't show up locally — must be tested separately, not assumed to work because localhost works.
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
