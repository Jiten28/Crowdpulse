# Architecture.md — CrowdPulse

## 1. Tech Stack (final — do not deviate mid-build)

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Data handling:** pandas (CSV parsing), Pydantic (validation/schemas)
- **GenAI:** Anthropic Claude API (`anthropic` SDK) — model `claude-sonnet-4-6`, called server-side only. (Swap to OpenAI only if the API key situation forces it — architecture below is provider-agnostic via a single `llm_client.py` wrapper.)
- **Frontend:** Server-rendered HTML (Jinja2 templates) + vanilla JS + Tailwind via CDN. No React/build step — keeps repo tiny and deploy trivial.
- **Storage:** In-memory (Python dict/session) for the current dataset + SQLite (single file, via `sqlite3` stdlib) for the incident log only. No external DB dependency.
- **Deployment:** Render (Web Service, free tier), same pattern as prior MediVerse AI deployment.
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
ANTHROPIC_API_KEY=
LLM_MODEL=claude-sonnet-4-6
MAX_UPLOAD_MB=2
RATE_LIMIT_CHAT_PER_MIN=10
```

## Final Architecture Status

The final implementation follows a lightweight FastAPI architecture designed for rapid deployment and maintainability.

Core Components:

- FastAPI backend
- Jinja2 server-side templates
- Vanilla JavaScript frontend
- SQLite incident log
- Provider-agnostic LLM wrapper
- Gemini Flash (default)
- CSV validation and parsing pipeline
- AI reasoning engine
- Operations chat service

Deployment:

- Render (Free Tier)
- Environment-variable based configuration
- Secure API key management

Status: Final implementation completed and successfully deployed.
