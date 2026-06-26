from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.platform.monitoring import MonitoringAlertsResponse, MonitoringOverviewResponse, PrometheusMonitoringClient
from app.db import models
from app.db.session import get_db

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class LLMOpsAgentUsage(BaseModel):
    agent_name: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class LLMOpsTelemetryResponse(BaseModel):
    found: bool
    service: str
    incident_id: str | None = None
    incident_key: str | None = None
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_estimated_cost_usd: float = 0.0
    agents: list[LLMOpsAgentUsage] = Field(default_factory=list)
    note: str | None = None


@router.get("/overview", response_model=MonitoringOverviewResponse, summary="Prometheus monitoring overview")
async def monitoring_overview():
    client = PrometheusMonitoringClient()
    return await client.get_overview()


@router.get("/alerts", response_model=MonitoringAlertsResponse, summary="Prometheus active alerts")
async def monitoring_alerts():
    client = PrometheusMonitoringClient()
    return await client.get_alerts()


@router.get("/llmops", response_model=LLMOpsTelemetryResponse, summary="Persisted LLMOps telemetry by service")
def monitoring_llmops(
    service: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    incident = (
        db.query(models.Incident)
        .join(models.Alert, models.Alert.id == models.Incident.alert_id)
        .filter(models.Alert.service_name == service)
        .order_by(models.Incident.created_at.desc())
        .first()
    )

    if not incident:
        return LLMOpsTelemetryResponse(
            found=False,
            service=service,
            note="No persisted incident telemetry found for this service yet.",
        )

    executions = (
        db.query(models.AgentExecution)
        .filter(models.AgentExecution.incident_id == incident.id)
        .order_by(models.AgentExecution.created_at.asc())
        .all()
    )

    usages: list[LLMOpsAgentUsage] = []
    for execution in executions:
        output_payload = execution.output_payload or {}
        llm_usage = output_payload.get("llm_usage") if isinstance(output_payload, dict) else None
        if not isinstance(llm_usage, dict):
            continue

        usages.append(
            LLMOpsAgentUsage(
                agent_name=llm_usage.get("agent_name") or execution.agent_name,
                model=str(llm_usage.get("model") or "unknown"),
                prompt_tokens=int(llm_usage.get("prompt_tokens") or 0),
                completion_tokens=int(llm_usage.get("completion_tokens") or 0),
                total_tokens=int(llm_usage.get("total_tokens") or 0),
                estimated_cost_usd=float(llm_usage.get("estimated_cost_usd") or 0.0),
            )
        )

    total_prompt_tokens = sum(item.prompt_tokens for item in usages)
    total_completion_tokens = sum(item.completion_tokens for item in usages)
    total_tokens = sum(item.total_tokens for item in usages)
    total_estimated_cost_usd = round(sum(item.estimated_cost_usd for item in usages), 6)

    return LLMOpsTelemetryResponse(
        found=bool(usages),
        service=service,
        incident_id=str(incident.id),
        incident_key=incident.incident_key,
        total_prompt_tokens=total_prompt_tokens,
        total_completion_tokens=total_completion_tokens,
        total_tokens=total_tokens,
        total_estimated_cost_usd=total_estimated_cost_usd,
        agents=usages,
        note=None if usages else "Incident found but no persisted llm_usage entries exist yet.",
    )
