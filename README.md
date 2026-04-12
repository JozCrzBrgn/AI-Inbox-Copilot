# AI Inbox Copilot

![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue)
![Security](https://img.shields.io/badge/Trivy-0%20CRITICAL-brightgreen)
![Bandit](https://img.shields.io/badge/Bandit-0%20issues-brightgreen)
![Dependabot](https://img.shields.io/badge/Dependabot-active-025E8C?logo=dependabot)

> Full-stack AI platform that analyzes customer support emails in real-time — extracting intent, priority, sentiment, and generating ready-to-send replies — shielded by a multi-layered LLM security pipeline, production-grade CI/CD, and 95% test coverage.

Built to demonstrate end-to-end engineering ownership: secure LLM integration, prompt injection defense, JWT-authenticated REST API, containerized deployment, and automated DevOps workflows aligned with US/remote engineering standards.

---

## Code Quality

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=JozCrzBrgn_AI-Inbox-Copilot)](https://sonarcloud.io/summary/new_code?id=JozCrzBrgn_AI-Inbox-Copilot)
![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen)
![Security](https://img.shields.io/badge/Bandit-0%20issues-brightgreen)

---

## Overview

AI Inbox Copilot solves a real operational bottleneck for Customer Service teams: manually triaging a high-volume inbox is slow and error-prone. This platform uses **OpenAI GPT models** with few-shot prompting to instantly classify each email by intent and urgency, generate a draft reply, and alert the team via **Slack** for high-priority cases — all persisted to **PostgreSQL** for auditing and history.

Before any email reaches the LLM, it passes through a **bespoke AI Security Layer** that detects and blocks prompt injection attacks, JSON poisoning, and role override attempts — a critical requirement for production LLM deployments.

The system comprises three independently containerized components:

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
| 🛡️ | **AI Security Layer** | Multi-layered defense: regex heuristics + semantic LLM validation block injections before they reach the model |
| 🎯 | **Few-Shot Prompting** | Versioned JSON prompt templates with configurable examples for consistent accuracy |
| 🚧 | **Rate Limiting** | Per-user throttling via SlowAPI, fully configurable via environment variables |
| 🔐 | **JWT + Argon2 Auth** | Short-lived tokens, Argon2-cffi password hashing (Password Hashing Competition winner) |
| 🔔 | **Slack Alerts** | Automatic webhook notifications triggered exclusively for high-priority cases |
| 🗄️ | **Email History** | PostgreSQL-backed audit trail with pageable retrieval endpoint |
| 🖥️ | **Web UI** | Dark/light mode, live analysis results, and history view built with Flet |
| 🐳 | **Docker Compose** | One-command startup with multi-stage builds, health checks, and dependency ordering |

---

## Architecture

```text
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
│                    FastAPI Backend                      │
│ JWT Auth · CORS · Rate Limiter                          │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
   ┌───────────▼──────────┐  ┌────────────▼────────────┐
   │  AI Security Layer   │  │     PostgreSQL 16       │
   └───────────┬──────────┘  └─────────────────────────┘
               │
   ┌───────────▼──────────┐
   │     Redis Layer      │──────▶ Token budgets & cache
   └───────────┬──────────┘
               │
   ┌───────────▼──────────┐
   │   OpenAI GPT API     │
   └───────────┬──────────┘
               │
   ┌───────────▼──────────┐
   │    Slack Webhook     │
   └──────────────────────┘
```

**Request flow:** JWT auth → rate limit check → **AI Security Pipeline** (regex scan → LLM semantic check → JSON poison detection) → prompt build with few-shot examples → GPT call → JSON normalize & Pydantic validate → PostgreSQL persist → Slack alert (optional) → structured JSON response.

---

## Tech Stack

**Application**

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Frontend | Flet (Python SPA, web renderer) |
| AI / LLM | OpenAI API — `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo` |
| Database | PostgreSQL 16, psycopg2 (parameterized queries only) |
| Cache    | Redis 7.4 |
| Auth | JWT (python-jose), Argon2 + PBKDF2 (passlib) |
| Config | pydantic-settings (typed settings, startup validation) |
| Notifications | Slack Incoming Webhooks |

**DevOps & Quality**

| Tool | Purpose |
|---|---|
| Docker + Docker Compose | Multi-stage builds, non-root containers, health checks |
| GitHub Actions | CI pipeline (lint → test → SonarCloud) + Security pipeline (Trivy → Bandit) |
| Ruff | Linting and import ordering enforcement |
| pytest + coverage | 170-test suite with ≥ 90% coverage gate (currently 100%) |
| SonarCloud | Cloud-based static analysis and blocking quality gate on `main` |
| Trivy | Container and filesystem CVE scanning (CRITICAL/HIGH severity) |
| Bandit | Python SAST — static security analysis |
| Dependabot | Automated dependency updates (pip, Docker, GitHub Actions) |
| Taskfile | Developer workflow automation (`cover`, `sort`, `bandit`, `validate-env`) |
| pyproject.toml | Centralized pytest configuration and warning filters |

---

## AI Security Layer

Every request to the analysis endpoint passes through `services/prompt_security.py` before the primary LLM is ever invoked. This pipeline guards against adversarial inputs that attempt to manipulate, override, or exfiltrate the system's behavior.

### Pipeline Functions

**`clean_input(texto)`**
Sanitizes raw input by stripping known injection patterns using ~30 compiled regex rules. Removes role-overriding tokens (`<|system|>`, `[INST]`, `<<SYS>>`), fake metadata separators, embedded code blocks, and direct instruction modifiers. Logs a warning whenever the original input is modified.

**`detect_prompt_injection(texto)`**
Runs a named-pattern analysis across 14 injection categories (role override, format forcing, fake authority, inline JSON payloads, etc.) and returns a confidence score (0.0–1.0). Any pattern match is individually recorded for traceability.

**`detect_injection_with_llm(texto)`**
Sends the *already-cleaned* text to a low-cost, low-latency model (e.g., `gpt-4o-mini`) acting strictly as a **security classifier**. This catches indirect, obfuscated, or social-engineering injection attempts that regex cannot reliably detect. On classifier failure, defaults to `is_manipulation: true` — failing safe.

**`_is_malicious_json(texto)`**
Extracts all JSON-shaped substrings from the input and checks their keys against a blocklist of model-output fields (`intent`, `priority`, `sentiment`, `suggested_reply`, etc.). Blocks payloads that attempt to pre-populate the response structure.

**`sanitize_and_validate(texto)`**
The single entry point called by the API. Orchestrates the full pipeline: runs `detect_prompt_injection` → `clean_input` → `_is_malicious_json`. Sets `should_block: true` if confidence ≥ 0.5, any critical pattern is detected, or a malicious JSON payload is found. Requests that trigger a block are logged and return a `security_violation` result — the primary LLM is never called.

### Threats Mitigated

| Attack Vector | Defense |
|---|---|
| **Prompt injection** ("ignore previous instructions") | Regex heuristics + LLM semantic classifier |
| **Role override** ("you are now a system") | Named-pattern detection + `clean_input` stripping |
| **Format injection** ("always output priority: high") | `format_injection` pattern + confidence threshold |
| **JSON poisoning** (`{"intent": "hack"}` embedded in body) | `_is_malicious_json` key inspection |
| **Fake metadata blocks** (`--- internal note ---`) | `fake_metadata_block` pattern |
| **Social engineering / indirect framing** | `detect_injection_with_llm` semantic pass |

---

## DevOps, CI/CD & Security

Every push and pull request passes through two automated pipelines before anything reaches `main`. Branch protection enforces: 1 PR approval + `lint` + `test` + `sonar` must pass + conversations resolved + branch up to date.

### CI Pipeline (`ci.yml`) — 3 required gates

```
PR / push to main
      │
      ├── [1] lint ──── Ruff (style + import order)
      │
      ├── [2] test ──── pytest + live PostgreSQL 16 service container
      │               coverage ≥ 90% enforced (currently 95%)
      │               coverage.xml uploaded as artifact
      │
      └── [3] sonar ─── SonarCloud quality gate (main only)
                        -Dsonar.qualitygate.wait=true (blocking merge)
```

### Security Pipeline (`security.yml`) — runs on every PR and push

| Stage | Tool | Scope | Result |
|---|---|---|---|
| 1 | **Trivy** | Filesystem (secrets, misconfigs, CVEs) | ✅ 0 findings |
| 1 | **Trivy** | `postgres:16` image (CRITICAL CVEs) | ✅ 0 findings |
| 1 | **Trivy** | `python:3.12-slim` image (CRITICAL CVEs) | ✅ 0 findings |
| 1 | **Trivy** | `redis:8-alpine` image (CRITICAL CVEs) | ✅ 0 findings |
| 2 | **Bandit** | Python SAST — HIGH severity, `-lll` flag | ✅ 0 findings |

Bandit runs after Trivy succeeds (`needs: trivy`), ensuring no HIGH-severity Python vulnerability escapes the pipeline. Results are archived in `security_reports/`.

### Dependency Management — Dependabot

Auto-opens grouped PRs monthly for `pip`, `docker`, and `github-actions`. Major version bumps are excluded. All Dependabot PRs must pass the full CI + Security pipeline before merge.

### Application Security Controls

| Control | Implementation |
|---|---|
| Non-root containers | Dedicated `appuser` in both backend and frontend Dockerfiles |
| Multi-stage Docker builds | Build tools stripped from final runtime image |
| Argon2 password hashing | Passlib `CryptContext` with PBKDF2 fallback |
| JWT validation | Min. 32-char secret enforced, restricted to HS256/384/512 |
| SQL injection prevention | Parameterized queries (`%s` placeholders) throughout — no f-string SQL |
| Input validation | Pydantic schemas enforce type safety at every API boundary |
| LLM prompt injection defense | Multi-layer AI Security pipeline (see section above) |
| Rate limiting | SlowAPI per-user throttle, limit configurable via `SEC_RATE_LIMIT` env var |
| Startup validation | pydantic-settings validates all config at boot — fails fast on misconfiguration |

---

## Testing

170 tests with **100% pass rate** and coverage enforced at ≥ 90% in CI.

### Strategy

- **Full isolation**: No test ever calls OpenAI, PostgreSQL, or Slack. All external dependencies are mocked via `monkeypatch` and `unittest.mock`.
- **Centralized fixtures**: `conftest.py` provides shared `mock_settings`, `mock_db`, and `app_client` fixtures, ensuring the app always boots with controlled configuration — not real `.env` secrets.
- **Import safety**: `backend.main` is imported lazily inside fixtures (after mocks are applied) to prevent premature module evaluation that would trigger real DB connections.
- **Security coverage**: `test_prompt_security.py` tests every branch of `clean_input`, `detect_prompt_injection`, `sanitize_and_validate`, and `_is_malicious_json` — including edge cases for empty inputs, high-confidence blocks, and JSON payload variants.
- **Coverage gate**: CI runs `coverage report --fail-under=90`; any regression below threshold blocks the merge.

### Running Tests Locally

```bash
# Full suite with coverage (uses Taskfile)
task cover

# Linting
task sort

# Python SAST
task bandit

# Audit
task audit

# Validate .env against .env.example
task validate-env
```

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
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

task sort      # Lint + import ordering
task cover     # Run tests + coverage report
uvicorn backend.main:app --reload
```
</details>

<details>
<summary>Key environment variables</summary>

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI key (`sk-...`) |
| `OPENAI_MODEL` | Primary model: `gpt-4o`, `gpt-4-turbo`, etc. |
| `OPENAI_CHEAP_MODEL` | Fast/cheap model for security checks: `gpt-4o-mini`, etc. |
| `SEC_JWT_SECRET` | Signing secret (≥ 32 chars) |
| `SEC_RATE_LIMIT` | Rate limit string, e.g. `5/minute` |
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

## Project Highlights

| Aspect | What it demonstrates |
|---|---|
| **LLM Security** | Regex heuristics + semantic LLM classifier + JSON poison detection — defense-in-depth for adversarial inputs |
| **API Design** | Versioned RESTful endpoints, JWT auth, configurable rate limiting, health checks, Pydantic validation |
| **Security Depth** | Argon2 hashing, parameterized SQL, non-root Docker, Trivy + Bandit = 0 findings |
| **DevOps Maturity** | Full CI/CD pipeline (lint → test → quality gate → security scan), 95% coverage enforced, Dependabot |
| **Production Thinking** | Startup config validation via pydantic-settings, multi-stage Docker builds, externalized prompts, structured logging |
| **Test Discipline** | 170 isolated tests, full OpenAI/DB mocking, centralized fixtures — fast and cost-free CI runs |

---

## Roadmap

- **Auth**: OAuth2 / SSO via Auth0 or GitHub OAuth
- **DB Migrations**: Alembic for schema versioning
- **Async DB**: asyncpg / SQLAlchemy async to match FastAPI's async model
- **LLM Abstraction**: Provider-agnostic interface (Anthropic, Gemini, Mistral)
- **Observability**: OpenTelemetry tracing + Prometheus metrics
- **Deployment**: Kubernetes manifests or Terraform IaC (AWS ECS / GCP Cloud Run)

---

## Author

**Josue Cruz** — Backend & AI Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-josuecruzbarragan-0077B5?logo=linkedin)](https://www.linkedin.com/in/josuecruzbarragan/)
[![GitHub](https://img.shields.io/badge/GitHub-JozCrzBrgn-181717?logo=github)](https://github.com/JozCrzBrgn)

*Building resilient, modern, and highly-scalable architectural solutions heavily fortified by advanced AI security pipelines.*  
*Licensed under the [MIT License](LICENSE).*
