# Runbook Guide

## Incident Handling
1. Alert is ingested and deduplicated
2. Incident is created or correlated
3. Agent graph executes context, RCA, impact, resolution, validation
4. Approval gate triggers for infrastructure-changing actions
5. Automation executes with dry-run and rollback support
6. Incident transitions through open -> investigating -> mitigating -> resolved -> closed

## Operational SLOs
- MTTA < 5 min
- MTTR < 45 min (P2)
- Automation success > 90%

## Failure Modes
- Kafka unavailable: queue to retry and DLQ
- LLM unavailable: fallback to deterministic runbook recommendations
- DB contention: switch to read replica and suspend low-priority workflows
