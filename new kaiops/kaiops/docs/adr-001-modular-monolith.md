# ADR-001: Modular Monolith First

## Status
Accepted

## Context
KaiOps requires enterprise speed with clear bounded contexts and a migration path to microservices.

## Decision
Adopt modular monolith architecture with strict module boundaries and event-driven internals.

## Consequences
- Faster initial delivery
- Lower operational complexity
- Straightforward extraction to services when scale requires
