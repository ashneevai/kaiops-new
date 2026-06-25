from typing import TypedDict


class AgentState(TypedDict):
    tenant_id: str
    incident_id: str
    alert: dict
    context: dict
    rca: dict
    impact: dict
    resolution: dict
    validation: dict
    approval: dict
    confidence: int
