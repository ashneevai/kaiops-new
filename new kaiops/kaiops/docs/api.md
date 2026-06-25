# API Documentation (Phase 3)

## Base URL
- /api/v1

## Core Endpoints
- POST /auth/token
- GET /alerts
- POST /alerts/ingest
- GET /incidents
- POST /incidents/{incident_id}/status/{status}
- GET /incidents/{incident_id}/metrics
- POST /agents/incidents/{incident_id}/execute
- GET /knowledge/retrieve?q=
- GET /workflows
- GET /approvals
- GET /automations
- GET /audit
- GET /users
- GET /notifications

## Security
- Bearer JWT
- Tenant context via x-tenant-id
- RBAC claims embedded in token
