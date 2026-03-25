# AI Inbox Copilot

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue)

> Full-stack AI platform that analyzes customer support emails in real-time — extracting intent, priority, sentiment, and generating ready-to-send replies — backed by a production-grade CI/CD pipeline, security scanning, and 96% test coverage.

Built to demonstrate end-to-end engineering ownership: LLM integration, secure REST API design, containerized deployment, and automated DevOps practices aligned with modern US/remote engineering standards.

---

## Code Quality
[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=JozCrzBrgn_AI-Inbox-Copilot)](https://sonarcloud.io/summary/new_code?id=JozCrzBrgn_AI-Inbox-Copilot)
![Coverage](https://img.shields.io/badge/Coverage-96%25-brightgreen)
![Security](https://img.shields.io/badge/Bandit-0%20issues-brightgreen)

---

## Overview

AI Inbox Copilot solves a real operational problem for Customer Service teams: manually triaging a high-volume inbox is slow and error-prone. This platform uses **OpenAI GPT models** with few-shot prompting to instantly classify each email by intent and urgency, generate a draft reply, and alert the team via **Slack** for high-priority cases — all persisted to **PostgreSQL** for audit and history.

The system is composed of three independently containerized services:

| Service | Technology | Port |
|---|---|---|
| REST API | FastAPI + Uvicorn (Python 3.12) | `8000` |
| Web UI | Flet (Python-based SPA) | `8550` |
| Database | PostgreSQL 16 | `5432` |

---

## Key Features

| | Feature | Highlight |
|---|---|---|
| 🤖 | **AI Email Analysis** | Extracts intent, priority, sentiment, summary, and a suggested reply via GPT |
| 🎯 | **Few-Shot Prompting** | Versioned JSON prompt templates with configurable examples for higher accuracy |
| 🔐 | **JWT + Argon2 Auth** | Short-lived tokens, Argon2 password hashing (Password Hashing Competition winner) |
| 🚦 | **Rate Limiting** | Per-user throttling via SlowAPI — abuse-resistant by design |
| 🔔 | **Slack Alerts** | Automatic notifications triggered only for high-priority emails |
| 🗄️ | **Email History** | PostgreSQL-backed audit trail with a pageable retrieval endpoint |
| 🖥️ | **Web UI** | Dark/light mode, live analysis results, and history view |
| 🐳 | **Docker Compose** | One-command startup with health checks and service dependency ordering |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User Browser                       │
└───────────────────────────┬─────────────────────────────┘
                            │ :8550
              ┌─────────────▼─────────────┐
              │     Flet Web Frontend     │
              │  Login · Analyze · History│
              └─────────────┬─────────────┘
                            │ REST :8000
┌───────────────────────────▼─────────────────────────────┐
│                  FastAPI Backend                        │
│                                                         │
│  POST /token     POST /v1/analyze    GET /v1/emails     │
│                                                         │
│        JWT Auth · Rate Limiter · CORS Middleware        │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
   ┌───────────▼──────────┐  ┌────────────▼────────────┐
   │   OpenAI GPT API     │  │     PostgreSQL 16       │
   │  (few-shot prompts)  │  │   emails history table  │
   └───────────┬──────────┘  └─────────────────────────┘
               │
   ┌───────────▼──────────┐
   │    Slack Webhook     │
   │  (high priority only)│
   └──────────────────────┘
```

**Request flow:** JWT auth → rate limit check → AI prompt build (system prompt + few-shot examples) → GPT call → JSON normalize & validate → PostgreSQL save → optional Slack alert → structured response.

---

## Tech Stack

**Application**

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Frontend | Flet (Python SPA, web renderer) |
| AI / LLM | OpenAI API — `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo` |
| Database | PostgreSQL 16, psycopg2 (parameterized queries) |
| Auth | JWT (python-jose), Argon2 + PBKDF2 (passlib) |
| Config | pydantic-settings (startup validation, typed settings) |
| Notifications | Slack Incoming Webhooks |

**DevOps & Quality**

| Tool | Purpose |
|---|---|
| Docker + Docker Compose | Multi-stage builds, non-root containers, health checks |
| GitHub Actions | CI (lint → test → SonarCloud) + Security (Trivy → Bandit) |
| Ruff | Linting and import ordering |
| pytest + coverage.py | Test suite with ≥ 90% coverage gate |
| SonarCloud | Static analysis and quality gate on `main` |
| Trivy | Container and filesystem CVE scanning |
| Bandit | Python SAST — static code security analysis |
| Dependabot | Automated dependency updates (pip, Docker, Actions) |
| Taskfile | Developer workflow automation |

---

## DevOps, CI/CD & Security

Every push and pull request passes through two automated pipelines before anything reaches `main`. No merge is possible without all quality gates passing.

### CI Pipeline (`ci.yml`) — 3 required gates

```
PR / push to main
      │
      ├── [1] Lint ──── Ruff (style + import order)
      │
      ├── [2] Test ──── pytest + real PostgreSQL 16 container
      │               coverage ≥ 90% enforced (current: 96%)
      │               coverage.xml uploaded as artifact
      │
      └── [3] Sonar ─── SonarCloud quality gate (main only)
                        sonar.qualitygate.wait=true (blocking)
```

Branch protection enforces: 1 PR approval + `lint` + `test` + `sonar` must pass + conversations resolved + branch up to date.

### Security Pipeline (`security.yml`) — runs on every PR and push

| Stage | Tool | Scope | Result |
|---|---|---|---|
| 1 | **Trivy** | Filesystem (secrets, misconfigs, CVEs) | ✅ 0 findings |
| 1 | **Trivy** | `postgres:16` image (CRITICAL CVEs) | ✅ 0 findings |
| 1 | **Trivy** | `python:3.12-slim` image (CRITICAL CVEs) | ✅ 0 findings |
| 2 | **Bandit** | Python SAST — HIGH severity | ✅ 0 findings |

> Results verified in `security_reports/` — 708 lines scanned, 0 HIGH/MEDIUM issues.

### Dependency Management — Dependabot

Auto-opens grouped PRs monthly for `pip`, `docker`, and `github-actions` — major version bumps excluded. All Dependabot PRs must pass the full CI pipeline to merge.

### Application Security Controls

| Control | Implementation |
|---|---|
| Non-root containers | Dedicated `appuser` in both Dockerfiles |
| Multi-stage builds | Build tools stripped from final image |
| Argon2 password hashing | Passlib `CryptContext` with PBKDF2 fallback |
| JWT validation | Min. 32-char secret, restricted to HS256/384/512 |
| SQL injection prevention | Parameterized queries (`%s` placeholders) throughout |
| Input validation | Pydantic schemas enforce type safety at the API boundary |
| Rate limiting | SlowAPI per-user throttle on AI endpoints |
| Startup validation | Pydantic-settings validates all config at boot — fails fast on misconfiguration |

---

## Installation & Setup

**Requirements:** Docker, Docker Compose, OpenAI API key.

```bash
git clone https://github.com/JozCrzBrgn/AI-Inbox-Copilot.git
cd AI-Inbox-Copilot

cp .env.example .env   # Fill in OPENAI_API_KEY, SEC_JWT_SECRET, DB_PASSWORD

docker compose up --build
```

| Service | URL |
|---|---|
| Web UI | http://localhost:8550 |
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

<details>
<summary>Local development (without Docker)</summary>

```bash
pip install -r requirements-dev.txt
ruff check .
coverage run --source=frontend,backend,prompts --omit="tests/*,mocks/*" -m pytest
coverage report --fail-under=90
uvicorn backend.main:app --reload
```
</details>

<details>
<summary>Key environment variables</summary>

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI key (`sk-...`) |
| `OPENAI_MODEL` | `gpt-4o`, `gpt-4-turbo`, etc. |
| `SEC_JWT_SECRET` | Signing secret (≥ 32 chars) |
| `SEC_AUTH_USERNAME` / `SEC_AUTH_PASSWORD` | Login credentials |
| `DB_HOST/PORT/NAME/USER/PASSWORD` | PostgreSQL connection |
| `SLACK_WEBHOOK_URL` | Slack alerts (optional) |
</details>

---

## Usage

```bash
# Authenticate
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin&password=your_password" | jq -r .access_token)

# Analyze an email
curl -X POST http://localhost:8000/v1/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_content": "Hi, I never received my order #12345 — it has been 2 weeks. Please help."}'
```

```json
{
  "customer_name": "Unknown",
  "intent": "Delivery complaint",
  "summary": "Customer reports non-delivery of order #12345 after two weeks.",
  "priority": "high",
  "sentiment": "negative",
  "suggested_subject": "RE: Your Order #12345 – We Are On It",
  "suggested_reply": "Dear Customer, we sincerely apologize..."
}
```

---

## Why This Project

| Aspect | What it demonstrates |
|---|---|
| **LLM Engineering** | Structured prompting, few-shot examples, JSON normalization, error recovery |
| **API Design** | RESTful versioned endpoints, JWT auth, rate limiting, health checks |
| **Security Depth** | Argon2 hashing, parameterized SQL, non-root Docker, Trivy + Bandit scan = 0 issues |
| **DevOps Maturity** | Full CI/CD pipeline, 96% coverage enforced, SonarCloud quality gate, Dependabot |
| **Production Thinking** | Startup config validation, multi-stage builds, health checks, externalized prompts |

---

## Roadmap

- **Auth**: OAuth2 / SSO via Auth0 or GitHub OAuth
- **DB Migrations**: Alembic for schema versioning
- **Async DB**: asyncpg / SQLAlchemy async to match FastAPI's async model
- **LLM Abstraction**: Provider-agnostic interface (Anthropic, Gemini)
- **Observability**: OpenTelemetry tracing + Prometheus metrics
- **Deployment**: Kubernetes manifests or Terraform IaC (AWS ECS / GCP Cloud Run)

---

## Author

**Josué Cruz** — Backend & AI Engineer

Python · FastAPI · LLMs · PostgreSQL · Docker · CI/CD

[![LinkedIn](https://img.shields.io/badge/LinkedIn-josuecruzbarragan-0077B5?logo=linkedin)](https://www.linkedin.com/in/josuecruzbarragan/)
[![GitHub](https://img.shields.io/badge/GitHub-JozCrzBrgn-181717?logo=github)](https://github.com/JozCrzBrgn)

---

*Licensed under the [MIT License](LICENSE).*
