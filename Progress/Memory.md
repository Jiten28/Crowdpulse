# Memory.md — CrowdPulse

**Purpose:** This file is the single source of truth for "what has actually been built so far." Any AI tool (Claude, ChatGPT, Cursor, etc.) picking up this project — in a new chat, or after switching models — must read this file FIRST, before PRD/Architecture/Rules/Phases, and before reading the codebase.

**Update rule:** update this file at the END of every work session or every completed phase, whichever comes first. Never leave it stale — a stale Memory.md is worse than no Memory.md, because it causes the next AI session to make wrong assumptions instead of asking.

**Read order for a new AI session:** Memory.md (this file) → Phases.md (what phase are we in) → Rules.md (boundaries) → relevant parts of Architecture.md/PRD.md as needed. Do not re-read the entire codebase file-by-file if this file already states what exists and works.

---

## Current Status
- Phases 0-4 complete and locally verified. Phase 5 mostly done. Phase 6 partially done.
- Last updated: 2026-07-17
- Deployed URL: not yet filled in, see README.md
- GitHub repo: not yet pushed

## Completed Phases
- Phase 0 Scaffold: done, health check verified.
- Phase 1 Data Ingestion and Dashboard: done, CSV upload/parsing/status calc all tested locally.
- Phase 2 GenAI Reasoning Engine: done, structured JSON validated, retry and graceful failure verified with an invalid key.
- Phase 3 Ops Chat: done, context injection and rate limiting implemented, structurally verified.
- Phase 4 Incident Log and Export: done and verified locally.
- Phase 5 Accessibility and Security: mostly done, not verified in an actual screen reader.

## In-Progress Phase
Phase 6 Tests and README and Polish: tests passing 18 of 18, README written. Still needed: deploy to Render with a real API key, verify actual AI output quality, fill in deployed link, push to GitHub, write LinkedIn post.

## Known Issues / Blockers
Fixed during build: anthropic SDK was initially pinned to an old version incompatible with the httpx it pulled in, causing a proxies keyword argument crash. Pinned to a current version instead, confirmed working.
LLM-dependent features have only been tested against an invalid key, confirming graceful failure. They have not been tested with a real key to confirm output quality. Do this before submitting.

## Key Decisions Log
_(append here as decisions are made or changed — do not delete old entries, strike them through instead so the reasoning history is preserved)_

- 2026-07-17: Scoped to persona = Organizer, verticals = Crowd Management + Operational Intelligence/Real-Time Decision Support. Reason: challenge brief explicitly names these; solo 2-day timeline requires narrow scope. See PRD.md §3.
- 2026-07-17: Stack finalized as FastAPI + Jinja2/vanilla JS + Tailwind CDN, no frontend framework, no vector DB. Reason: repo size limit (10MB) and efficiency grading criterion. See Architecture.md §4.

## File Manifest (update as files are created — helps a new session know what exists without listing the directory)
```
[ ] app/main.py
[ ] app/config.py
[ ] app/models/schemas.py
[ ] app/services/data_store.py
[ ] app/services/csv_parser.py
[ ] app/services/llm_client.py
[ ] app/services/reasoning_engine.py
[ ] app/services/chat_service.py
[ ] app/services/incident_log.py
[ ] app/routes/upload.py
[ ] app/routes/dashboard.py
[ ] app/routes/ai.py
[ ] app/routes/incidents.py
[ ] app/templates/*
[ ] app/static/app.js
[ ] data/sample_gate_data.csv
[ ] tests/*
[ ] README.md
[ ] requirements.txt / .env.example / .gitignore / deployment config
```
(Check items off as they're created AND working — not just created. A file that exists but isn't wired up or tested is still `[ ]`.)

## Next Action for Whoever Picks This Up
Start Phase 0 (Scaffold) per Phases.md. Nothing exists yet — this is a clean start.

---
### Template for future entries (copy this block when updating)
```
## Update — [date]
**Phase completed:** [phase name/number]
**What works (verified, not assumed):** ...
**What's incomplete/stubbed:** ...
**Deviations from Architecture/Rules/Design docs (and why):** ...
**Next action:** ...
```
