# Developer Guide

## Backend
1. cd apps/api
2. pip install -e .[dev]
3. alembic upgrade head
4. uvicorn app.main:app --reload

## Frontend
1. cd apps/web
2. npm install
3. npm run dev

## Test Strategy
- Unit tests for each module service and platform utilities
- Integration tests for API contracts and persistence
- E2E tests for primary operator workflows

## Coding Standards
- Typed Python and strict TypeScript
- Module-level ownership and bounded contexts
- Event contracts versioned and backward compatible
