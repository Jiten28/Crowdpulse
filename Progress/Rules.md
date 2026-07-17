# Rules.md — CrowdPulse

These are hard boundaries for any AI tool (Claude, ChatGPT, Cursor, etc.) working on this codebase. Read this before writing or changing any code. If a request conflicts with these rules, flag the conflict instead of silently overriding a rule.

## 1. Allowed Libraries

- Backend: `fastapi`, `uvicorn`, `pydantic`, `pandas`, `python-dotenv`, `google-genai` (single GenAI provider — do not add a second provider SDK unless the first is fully removed first, never carry two simultaneously), `python-multipart` (file upload), `jinja2`, stdlib `sqlite3`
- Frontend: vanilla JS, Tailwind CDN. No jQuery, no frontend framework, no bundler/build step.
- Testing: `pytest`, `pytest-mock`

## 2. Explicitly Forbidden

- No ORMs (SQLAlchemy, etc.) — the incident log is one table, raw `sqlite3` is enough
- No React/Vue/Angular or any Node build pipeline — repo must stay small and deploy-simple
- No vector databases / embeddings — dataset size doesn't justify it (see Architecture.md §4)
- No hardcoded API keys, prompts with secrets embedded, or committed `.env` files
- No mock/fake GenAI responses in the actual app code — mocking is allowed only inside `tests/`, never in `services/reasoning_engine.py` or `chat_service.py` at runtime
- No scope expansion into other verticals (navigation, transport, sustainability, multilingual, fan-facing features) without explicit sign-off — re-read PRD.md §3 before adding any feature
- Do not write more code than the feature needs. No speculative abstraction, no unused config toggles, no "just in case" endpoints.

## 3. Error Handling Standards

- Every external call (LLM API, file parsing) wrapped in try/except with a specific, user-facing error — never a bare `except: pass`
- CSV upload: validate file type, size (`MAX_UPLOAD_MB`), and required columns before processing. Reject with a clear 400 message on failure, don't crash.
- LLM JSON parsing: validate against the Pydantic schema; on failure, retry once with a stricter instruction, then degrade gracefully (UI shows "AI assessment temporarily unavailable" — never fabricate a fallback risk score)
- All routes return proper HTTP status codes (400 for bad input, 422 for validation, 500 only for genuine server errors, 429 for rate limit)

## 4. Security Rules

- API keys only via environment variables, loaded through `config.py`, never referenced directly in route/service files
- `.env` in `.gitignore` from commit #1; `.env.example` committed instead with empty values
- Sanitize/limit length of chat input before it's interpolated into any prompt (prevents prompt injection from trivially overriding system instructions — mention this defense in the README)
- Rate limit `/ai/chat` and `/ai/brief` to prevent API cost abuse (default: 10 requests/min/IP)
- CORS: restrict to the deployed origin in production, not `*`

## 5. Code Style

- PEP8, type hints on all function signatures, docstrings on every service function (what it does, params, return shape)
- Keep functions short and single-purpose; if a route handler exceeds ~25 lines, extract logic into `services/`
- No commented-out dead code left in commits

## 6. Testing Requirements

- `test_csv_parser.py`: valid file, missing columns, empty file, oversized file, wrong file type
- `test_data_store.py`: correct occupancy % calc, status thresholds (Normal/Watch/Critical)
- `test_reasoning_engine.py`: prompt construction is correct given sample data; JSON parsing handles both valid and malformed LLM output (mock the LLM call — do not hit the real API in automated tests)
- Manual test checklist (documented in README, since LLM output varies): upload sample CSV → dashboard renders → trigger AI brief → ask 3 sample chat questions → log an incident → export CSV

## 7. Repo Hygiene (10MB limit is a hard submission requirement)

- `.gitignore` must exclude: `__pycache__/`, `*.pyc`, `.env`, `venv/`, `.pytest_cache/`, any `node_modules` (shouldn't exist anyway), `*.db` if it grows large during dev
- No committed sample datasets larger than a few KB — `sample_gate_data.csv` should be realistic but small (~20-40 rows is plenty)
- No committed screenshots/videos in the repo — those go in the LinkedIn post, not git

## 8. GenAI Usage Rule (this is what the judges are checking for)

- The LLM must receive real data and produce non-deterministic, reasoning-based output (risk assessment text, recommendation text, chat answers) — not just fill in a hardcoded template
- If in doubt whether a feature "really" uses GenAI or is faking it: ask "if I removed the LLM call, would this feature still produce this exact output?" If yes, it's not really using GenAI — fix it before submission.

## Final Compliance Checklist

| Requirement          | Status             |
| -------------------- | ------------------ |
| GenAI Integration    | ✓                  |
| Working Deployment   | ✓                  |
| GitHub Repository    | ✓                  |
| Public Repository    | ✓                  |
| CSV Evaluator Upload | ✓                  |
| Operational Persona  | ✓                  |
| Focused Verticals    | ✓                  |
| Testing              | ✓                  |
| Documentation        | ✓                  |
| README               | ✓                  |
| LinkedIn Post        | Pending Submission |
