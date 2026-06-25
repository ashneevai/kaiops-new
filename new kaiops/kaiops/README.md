# KaiOps Next Gen Platform

KaiOps is an enterprise AIOps Incident Management and Autonomous Operations platform.

## Monorepo Structure

- apps/web: Next.js 15 frontend
- apps/api: FastAPI modular monolith backend
- services/*: domain modules (models, schemas, repository, service, api, tests)
- agents/*: AI agent runtime components
- platform/*: cross-cutting platform capabilities (auth, telemetry, messaging, cache)
- infrastructure/*: Docker, Kubernetes, Terraform
- docs/*: ADRs, developer, API, deployment and runbook documentation
- tests/*: cross-system integration and end-to-end tests

## Quick Start

1. Start infrastructure:
   - `docker compose -f infrastructure/docker/docker-compose.yml up -d`
2. Backend:
   - `cd apps/api`
   - `pip install -e .`
   - `alembic upgrade head`
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. Frontend:
   - `cd apps/web`
   - `npm install`
   - `npm run dev`

## Windows Local Run Without Docker

Run the PowerShell launcher from the repo root:

```powershell
.\scripts\run-local.ps1 -InstallFrontendDeps
```

The script starts the API immediately and starts the frontend if Node.js/npm are installed. If you do not have local PostgreSQL, Redis, and Kafka, point the `.env` settings to managed or remote services before starting the API.

## Quality Gates

- Unit + integration tests required on every PR
- Security scans (SAST + dependency scanning)
- OpenTelemetry traces and Prometheus metrics required in all runtime components
- 90%+ coverage target
