# KaiOps Architecture (Phase 1)

## Style
- Modular monolith backend (FastAPI + SQLAlchemy)
- Event-driven internals (Kafka topics + DLQ)
- Agentic incident runtime (LangGraph)
- RAG-backed knowledge retrieval

## Core Runtime
- apps/api: API + orchestration + platform capabilities
- services/*: bounded domain modules
- agents/*: reasoning graph components
- platform/*: auth, telemetry, messaging, cache

## Module Boundaries
- Alert Management
- Incident Management
- Workflow Management
- Approval Management
- Automation Management
- Knowledge Management
- AI Agent Runtime
- Audit Management
- User Management
- Notification Management

## Non-Functional
- Multi-tenant
- Auditable
- Observable (OTel, Prometheus)
- Cloud-native deployment (Docker/Kubernetes/Terraform)
