# CrowdPulse — GenAI Crowd Command Center for Tournament Organizers

> **CrowdPulse** is a GenAI-powered operational decision-support dashboard that helps tournament organizers monitor crowd density, identify high-risk zones, and receive AI-generated recommendations during FIFA World Cup–scale events.

Built for **PromptWars Virtual — Challenge 4: Smart Stadiums & Tournament Operations**

**Persona:** Tournament Organizer

**Primary Verticals:**

- Crowd Management
- Operational Intelligence
- Real-Time Decision Support

---

## Live Demo

**GitHub Repository**

https://github.com/Jiten28/Crowdpulse

**Live Deployment**

https://crowdpulse-70bq.onrender.com

---

# Overview

CrowdPulse gives tournament organizers a real-time operational view of stadium gates and crowd density.

Instead of simply displaying occupancy statistics, the application uses Generative AI to analyze live operational data and produce actionable recommendations for crowd management.

The application supports:

- Crowd monitoring
- AI-generated operational briefs
- Incident logging
- CSV-based evaluator testing
- Natural language operational chat

---

# Why CSV Upload?

The PromptWars Challenge specifically recommends allowing evaluators to upload data when real-world live feeds are unavailable.

Instead of relying on unavailable IoT infrastructure, CrowdPulse ships with a realistic dataset:

```
data/sample_gate_data.csv
```

This allows judges to test the complete workflow in under one minute.

---

# Features

## Crowd Monitoring

- Live occupancy percentages
- Entry-rate monitoring
- Capacity calculations
- Automatic risk classification

Status Levels

- Normal
- Watch
- Critical

---

## AI Ops Brief

Flagged zones are automatically analyzed using Gemini.

The AI returns structured operational recommendations including:

- Risk level
- Operational reasoning
- Recommended action
- Urgency level

Responses are validated before rendering.

---

## Ops Chat

Organizers can ask natural language questions such as:

- Which gates are critical?
- Which zone needs immediate attention?
- What should we do about South Gate?

Responses are grounded on the uploaded dataset rather than generic LLM knowledge.

---

## Incident Log

Recommendations can be marked as actioned.

The application stores:

- timestamp
- location
- recommendation
- severity

The log can be exported as CSV.

---

# GenAI Usage

Generative AI is a core part of CrowdPulse.

It is not used for decorative text generation.

### AI Ops Brief

```
app/services/reasoning_engine.py
```

The application sends actual occupancy and entry-rate data to Gemini using a structured prompt.

The response must follow a predefined JSON schema before being accepted.

---

### Ops Chat

```
app/services/chat_service.py
```

Every user question includes the currently loaded stadium data as context, ensuring responses remain grounded in the uploaded dataset.

---

# Tech Stack

Backend

- FastAPI
- Python

Frontend

- Jinja2
- HTML
- CSS
- Vanilla JavaScript

AI

- Google Gemini Flash

Database

- SQLite

Deployment

- Render

Testing

- Pytest

---

# Project Structure

```
app/
data/
tests/
static/
templates/
Architecture.md
Memory.md
PRD.md
README.md
requirements.txt
render.yaml
```

---

# Local Setup

Clone the repository

```bash
git clone https://github.com/Jiten28/Crowdpulse
cd Crowdpulse
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Copy environment variables

```bash
cp .env.example .env
```

Run

```bash
uvicorn app.main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

# Deployment

CrowdPulse is deployed on Render.

Configure:

- GEMINI_API_KEY
- LLM_PROVIDER=gemini

The application automatically uses the latest supported Gemini Flash model.

---

# Evaluator Guide

1. Open the deployed application.

2. Upload

```
data/sample_gate_data.csv
```

3. Verify dashboard population.

4. Click

```
Generate AI Brief
```

5. Verify AI recommendations.

6. Open Ops Chat.

Example questions:

- Which gates are critical right now?
- What should we do about the busiest zone?

7. Mark a recommendation as actioned.

8. Verify Incident Log.

9. Export CSV.

10. Upload an invalid file to verify validation.

---

# Running Tests

Run

```bash
pytest tests/ -v
```

Current automated test coverage includes:

- CSV validation
- Invalid uploads
- Capacity calculations
- Status classification
- Occupancy sorting
- Empty datasets
- LLM response validation
- Retry behaviour
- JSON schema validation

All tests pass.

```
18 passed
```

---

# Security

- Environment variables stored outside the repository
- API keys never committed
- File size validation
- CSV validation
- Prompt injection mitigation
- JSON schema validation
- Rate limiting
- Configurable CORS
- Input sanitization

---

# Accessibility

- Keyboard accessible
- Visible focus states
- Semantic labels
- aria-live announcements
- Status communicated with icons and text
- WCAG-aware color contrast

---

# Architecture

See

```
Architecture.md
```

for detailed system architecture.

---

# Scope

This project intentionally focuses on:

- Tournament Organizers
- Crowd Management
- Operational Intelligence

Features such as transportation, sustainability, volunteer management, multilingual UI, and fan navigation were intentionally excluded to maintain a focused end-to-end solution.

---

# License

Created for **PromptWars Virtual — Challenge 4**.
