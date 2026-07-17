# Phases.md — CrowdPulse

Deadline is 19/07/2026 11:59 PM IST — roughly 2 days from project start. Phases are sized accordingly: small, sequential, each one leaves the app in a working (if incomplete) state. Do not start a phase until the previous one's "Definition of Done" is met. Update `Memory.md` after every phase.

## Phase 0 — Scaffold (30-45 min)
**Goal:** Empty but running FastAPI app deployed to Render.
- Create folder structure per Architecture.md §3
- `requirements.txt`, `.env.example`, `.gitignore`
- Minimal `main.py` with `/health` route
- Push to GitHub, connect Render, confirm live deploy URL works
**Definition of Done:** `/health` returns 200 on the live Render URL.

## Phase 1 — Data Ingestion + Dashboard (skeleton) (1-1.5 hr)
**Goal:** Upload a CSV, see it rendered as a table.
- `services/csv_parser.py` + `models/schemas.py` (ZoneReading)
- `services/data_store.py` (in-memory store, occupancy % calc, status thresholds)
- `routes/upload.py`, `routes/dashboard.py`
- `templates/dashboard.html` with Tailwind CDN, renders zone cards from data
- Ship `data/sample_gate_data.csv`
**Definition of Done:** Uploading the sample CSV shows correct per-zone occupancy % and status (Normal/Watch/Critical) on the live deployed dashboard.

## Phase 2 — GenAI Reasoning Engine (1.5-2 hr — this is the core feature, don't rush it)
**Goal:** "AI Ops Brief" panel showing real LLM-generated risk assessments and recommendations.
- `services/llm_client.py` (provider-agnostic wrapper)
- `services/reasoning_engine.py`: builds structured prompt from current zone data, calls LLM, validates/parses JSON response against schema
- `routes/ai.py` → `POST /ai/brief`
- Render results in dashboard as a distinct "AI Ops Brief" section (not mixed into raw data table)
- Handle and visibly display the graceful-failure state (bad JSON / API error)
**Definition of Done:** Clicking "Generate AI Brief" on the live deployed app produces real, data-grounded risk/recommendation text that changes appropriately when the uploaded CSV changes (test with two different sample CSVs to confirm it's not hardcoded).

## Phase 3 — Ops Chat (1-1.5 hr)
**Goal:** Natural-language Q&A grounded in current data.
- `services/chat_service.py`: injects current dataset summary as context, sends user question, returns answer
- `routes/ai.py` → `POST /ai/chat`
- `static/app.js` chat widget (input box, message history, fetch call)
- Input sanitization + length limit before prompt interpolation
- Rate limiting on this endpoint
**Definition of Done:** At least 3 distinct question types work correctly and are grounded in the actual uploaded data (verify by changing the data and re-asking the same question).

## Phase 4 — Incident Log + Export (45 min - 1 hr)
**Goal:** Organizer can mark a recommendation as actioned and export the log.
- `services/incident_log.py` (sqlite, single table)
- `routes/incidents.py` → `POST /incidents`, `GET /incidents/export`
- UI: "Mark as Actioned" button on each AI recommendation, simple log view, export button
**Definition of Done:** Actioning a recommendation persists it; export produces a valid CSV with timestamp, zone, action, and status.

## Phase 5 — Accessibility + Security Pass (45 min - 1 hr)
**Goal:** Address the graded parameters that are easy to lose points on if skipped.
- Run through Rules.md §4 (security) and PRD.md §6 (accessibility) as checklists
- Add ARIA labels, check color contrast, confirm keyboard navigation works on chat + upload + buttons
- Confirm `.env` is not in git history, confirm rate limiting works, confirm CORS is scoped
**Definition of Done:** Manual checklist in README fully checked off.

## Phase 6 — Tests + README + Polish (1-1.5 hr)
**Goal:** Submission-ready.
- Write/finish tests per Rules.md §6, run `pytest`, all green
- Write README.md: what it does, architecture summary, how to test (including that sample CSV upload is the intended evaluator path), setup instructions, deployed link, note on GenAI usage explaining what's model-generated vs deterministic
- Final repo size check (`du -sh .git` and full folder) — must be < 10MB
- Record LinkedIn post content (technical approach explanation) per submission requirements
**Definition of Done:** Fresh clone + `pip install -r requirements.txt` + run instructions work exactly as documented; repo confirmed under 10MB; deployed link confirmed working from an incognito browser.

## Buffer
No dedicated buffer phase is scheduled given the timeline — if running behind, cut Phase 4 (Incident Log) down to just "mark as actioned" without CSV export before cutting anything from Phase 2 or 3 (those are the GenAI core and cannot be thin).

## Explicitly Deferred (do not attempt unless all phases above are done early)
- Multiple LLM providers with runtime switching
- Historical trend charts across multiple uploads
- Any second vertical or persona
