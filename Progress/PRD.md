# PRD.md — CrowdPulse: GenAI Crowd Command Center for Tournament Organizers

## 1. Context

Submission for **PromptWars Virtual — Challenge 4: Smart Stadiums & Tournament Operations** (FIFA World Cup 2026 theme). Individual, prompt-driven, GenAI-mandatory build. Evaluated by AI on: Code Quality, Security, Efficiency, Testing, Accessibility, Problem Statement Alignment.

**Deadline:** 19/07/2026, 11:59 PM IST. Repo must be < 10MB. Must include a working deployed link + LinkedIn post.

## 2. Problem Statement (as given)

Build a GenAI-enabled solution that enhances stadium operations and the tournament experience for fans, organizers, volunteers, or venue staff — leveraging Generative AI for navigation, crowd management, accessibility, transportation, sustainability, multilingual assistance, operational intelligence, or real-time decision support during FIFA World Cup 2026.

## 3. Scope Decision (deliberately narrow — per challenge guidance: "don't solve every problem")

- **Persona:** Tournament **Organizer** (stadium operations control room staff)
- **Verticals (max 2):** Crowd Management + Operational Intelligence / Real-Time Decision Support
- **Explicitly out of scope:** fan-facing features, transportation, sustainability, multilingual UI, volunteer tools. Not because they don't matter — because a solo, 2-day build that tries to cover all of them will be shallow everywhere and score worse than one thing done well.

## 4. Target User

A stadium operations organizer monitoring multiple gates/zones during a match, who needs to:

- See current crowd density per gate/zone at a glance
- Get AI-generated, prioritized action recommendations when congestion risk rises
- Ask free-form questions in natural language and get answers grounded in the current data (not generic chatbot fluff)

## 5. Core Features (MVP — must all work end-to-end)

### F1. Data Ingestion (simulated real-time feed)

- Organizer uploads a CSV of gate/zone readings: `timestamp, gate_id, zone_name, current_count, capacity, entry_rate`
- App validates and parses it; a sample CSV ships in the repo so evaluators can test without hunting for data (this satisfies the video's explicit "must provide test data if real-time isn't available" requirement)

### F2. Live Dashboard

- Table/card view of all gates: current occupancy %, status (Normal / Watch / Critical), trend arrow
- Simple visual (bar or heat-style) — no heavy charting library needed, keep it light

### F3. GenAI Reasoning Engine (the mandatory, must-be-real part)

- On each data refresh (or on-demand), the backend sends the current zone data to an LLM with a **structured system prompt** instructing it to reason over the data and return **structured JSON**: `{zone, risk_level, reasoning, recommended_action, urgency}`
- This is NOT a hardcoded if/else risk calculator with a GenAI label slapped on — the LLM must receive the actual numeric data and produce the risk assessment and recommendation itself. Deterministic pre-checks (e.g., occupancy > 90%) may flag a zone for _inclusion_ in the prompt, but the assessment and action text must come from the model.
- Recommendations rendered in the dashboard as an "AI Ops Brief" panel

### F4. Natural-Language Ops Chat

- Chat box: organizer types a question ("Which gates are critical right now?", "What should I do about Zone C?")
- Backend injects current dataset as context into the prompt (RAG-lite: no vector DB needed for this data size — direct context injection is correct here) and returns a grounded answer
- Must handle at least: status queries, "what should I do" queries, and a graceful reply when asked something outside the data's scope

### F5. Incident Log / Export

- Every AI-generated recommendation the organizer "acts on" gets logged with timestamp
- Exportable as CSV — gives the app a persistence/output artifact beyond just a chat window

## 6. Non-Functional Requirements

- **Security:** no hardcoded API keys, `.env` + `.gitignore`, uploaded CSV size/type validated, chat input sanitized before reaching prompt, basic rate limiting on the chat endpoint
- **Accessibility:** WCAG AA color contrast, all interactive elements keyboard-navigable, ARIA labels on dashboard status indicators, no color-only status signaling (icon + text too)
- **Efficiency:** no unnecessary dependencies, no dead code, LLM calls should send minimal necessary context (not the whole conversation history each time unless needed)
- **Testing:** core parsing/risk-flagging logic covered by unit tests; documented manual test steps for the GenAI-dependent paths (since LLM output isn't perfectly deterministic)

## 7. Success Criteria (mapped to the grading parameters)

| Grading Parameter           | How this project satisfies it                                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Problem Statement Alignment | Directly implements "operational intelligence" + "real-time decision support" + "crowd management" as named in the brief |
| GenAI Mandatory Use         | Core feature (F3) is impossible without the LLM; not decorative                                                          |
| Code Quality                | Small, focused FastAPI app; typed, documented, no scope creep                                                            |
| Security                    | Env-based secrets, input validation, sanitization, rate limiting                                                         |
| Efficiency                  | Lean stack, minimal deps, lightweight frontend, small repo                                                               |
| Testing                     | Unit tests for deterministic logic + manual test script for AI paths                                                     |
| Accessibility               | WCAG-aware markup and contrast                                                                                           |

## 8. Out of Scope / Explicit Non-Goals

- Real IoT/turnstile integration (CSV upload simulates this — clearly disclosed in the README, not hidden)
- User authentication/multi-tenant orgs
- Mobile app
- Any vertical beyond the two chosen

## Final Outcome

All planned MVP features have been completed successfully.

Completed Deliverables:

- CSV Upload
- Crowd Monitoring Dashboard
- AI Operations Brief
- Incident Logging
- Export CSV
- Ops Chat
- Render Deployment
- Automated Testing
- Documentation
- Security Hardening

Out-of-scope items remain intentionally excluded to preserve a focused solution.
