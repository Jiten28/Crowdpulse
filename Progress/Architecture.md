# Architecture.md — CrowdPulse

## 1. Tech Stack (final — do not deviate mid-build)

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Data handling:** pandas (CSV parsing), Pydantic (validation/schemas)
- **GenAI:** Google Gemini API (`google-genai` SDK) — model `gemini-flash-lite-latest` (Google's self-updating Flash-Lite alias), called server-side only, via a single `llm_client.py` wrapper. Chosen over Anthropic because it has a genuine no-credit-card free tier suitable for a zero-budget submission, and its higher daily quota (vs. the newer flagship Flash tier) suits this app's short, structured tasks well. An earlier draft of this app briefly supported Anthropic Claude as a second provider behind a runtime switch; that path was removed once Gemini proved sufficient, since carrying an unused second SDK and branching logic added complexity without benefit (see Rules.md — one provider at a time, not both).
- **Frontend:** Server-rendered HTML (Jinja2 templates) + vanilla JS + Tailwind via CDN. No React/build step — keeps repo tiny and deploy trivial.
- **Storage:** In-memory (Python dict/session) for the current dataset + SQLite (single file, via `sqlite3` stdlib) for the incident log only. No external DB dependency.
- **Deployment:** Render (Web Service, free tier).
- **Testing:** `pytest`

## 2. High-Level Flow

```
[CSV Upload] → [Parser/Validator] → [In-memory DataStore]
                                          │
                        ┌─────────────────┼─────────────────┐
                        ▼                                    ▼
              [Dashboard Renderer]                 [GenAI Reasoning Engine]
              (status per zone,                    (sends zone data → LLM →
               computed % occupancy)                 structured JSON risk +
                        │                             recommendation)
                        ▼                                    │
                 [Dashboard HTML] ◄──────── AI Ops Brief ─────┘
                        │
                        ▼
                 [Ops Chat Endpoint] → injects current data as context
                        │              → LLM answers in natural language
                        ▼
                 [Incident Log] ← organizer marks recommendation "actioned"
                        │
                        ▼
                 [CSV Export]
```

## 3. Folder Structure

```
crowdpulse/
├── app/
│   ├── main.py                # FastAPI app, route registration
│   ├── config.py               # env var loading (API keys, settings)
│   ├── models/
│   │   └── schemas.py          # Pydantic models: ZoneReading, RiskAssessment, ChatMessage
│   ├── services/
│   │   ├── data_store.py       # in-memory current dataset + helpers
│   │   ├── csv_parser.py       # upload validation + parsing
│   │   ├── llm_client.py       # provider-agnostic GenAI wrapper
│   │   ├── reasoning_engine.py # builds prompt from data → calls llm_client → parses structured JSON
│   │   ├── chat_service.py     # builds context-injected prompt for ops chat
│   │   └── incident_log.py     # sqlite read/write for logged actions
│   ├── routes/
│   │   ├── upload.py           # POST /upload
│   │   ├── dashboard.py        # GET /  (renders dashboard)
│   │   ├── ai.py                # POST /ai/brief, POST /ai/chat
│   │   └── incidents.py        # POST /incidents, GET /incidents/export
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── partials/
│   │       ├── zone_card.html
│   │       └── chat_widget.html
│   └── static/
│       └── app.js              # fetch calls, chat UI logic, no framework
├── data/
│   └── sample_gate_data.csv    # ships with repo so evaluators can test immediately
├── tests/
│   ├── test_csv_parser.py
│   ├── test_data_store.py
│   └── test_reasoning_engine.py  # mocks the LLM call, tests prompt construction + JSON parsing
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md                   # setup, deployed link, sample data explanation, architecture summary
└── Procfile / render.yaml      # deployment config
```

## 4. Key Design Decisions

- **Direct context injection over RAG/vector DB:** dataset per upload is small (dozens of zones, not thousands of documents). A vector DB would be over-engineering — "efficiency" is a graded parameter, and unnecessary infrastructure hurts that score, not helps it.
- **Structured JSON output from the LLM:** the reasoning engine prompt explicitly instructs the model to return JSON matching a fixed schema. This is validated with Pydantic on the way back in; if parsing fails, the app retries once, then falls back to a clearly-labeled "AI response unavailable" state — never silently fakes data.
- **Provider-agnostic `llm_client.py`:** single function `generate(system_prompt, user_prompt, json_mode=True)`. If the API key isn't available at demo time, the rest of the app is unaffected and this is the only file touched.
- **No client-side API keys, ever.** All LLM calls happen server-side.

## 5. API Endpoints

| Method | Path                | Purpose                                           |
| ------ | ------------------- | ------------------------------------------------- |
| GET    | `/`                 | Dashboard page                                    |
| POST   | `/upload`           | Upload/replace CSV dataset                        |
| POST   | `/ai/brief`         | Trigger GenAI reasoning pass over current data    |
| POST   | `/ai/chat`          | Ops chat — natural language Q&A over current data |
| POST   | `/incidents`        | Log an actioned recommendation                    |
| GET    | `/incidents/export` | Download incident log as CSV                      |
| GET    | `/health`           | Health check for deployment                       |

## 6. Environment Variables (`.env`, never committed)

```
GEMINI_API_KEY=
GEMINI_MODEL=gemini-flash-lite-latest
MAX_UPLOAD_MB=2
RATE_LIMIT_CHAT_PER_MIN=10
```

## Final Architecture Status

Implementation matches the plan above with one deliberate simplification made mid-build: the dual-provider (Anthropic + Gemini) design was reduced to Gemini-only once it proved sufficient and reliable, removing an unused SDK dependency and a code branch that never ran in the deployed app. `llm_client.py` still exposes a single provider-agnostic interface (`generate()` / `generate_json()`), so a second provider could be reintroduced later without touching `reasoning_engine.py` or `chat_service.py` — the abstraction was kept, the redundant implementation was not.

Status: Deployed and verified against the live Render URL, including CSV upload, AI Ops Brief, Ops Chat, incident logging, and CSV export.
