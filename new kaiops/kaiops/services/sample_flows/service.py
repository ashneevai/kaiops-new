from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from services.llm import AlertInput, IncidentAnalysis, IncidentAnalyst, LLMUnavailableError
from services.sample_flows.data import CATALOG

logger = logging.getLogger(__name__)

DEFAULT_FLOW_ID = "payment-latency"


def list_flows() -> list[dict[str, str]]:
    rows = [
        {
            "id": catalog_id,
            "alert_id": catalog_id.upper(),
            "alert_name": entry["name"],
            "alert_type": entry["source"],
            "title": entry["title"],
            "service": entry["service"],
            "severity": entry["severity"],
            "recommended_action": "Triage with KaiOps Incident Intelligence",
            "description": entry["description"],
        }
        for catalog_id, entry in CATALOG.items()
    ]
    return sorted(rows, key=lambda item: (item["service"].lower(), item["title"].lower()))


def _alert_from_catalog(flow_id: str) -> tuple[str, AlertInput]:
    resolved_flow_id = flow_id if flow_id in CATALOG else DEFAULT_FLOW_ID
    entry = CATALOG[resolved_flow_id]
    alert = AlertInput(
        name=entry["name"],
        service=entry["service"],
        severity=entry["severity"],
        description=entry["description"],
        source=entry["source"],
        labels=dict(entry.get("labels", {})),
        annotations=dict(entry.get("annotations", {})),
    )
    return resolved_flow_id, alert


def _normalize_alert_input(payload: dict[str, Any]) -> AlertInput:
    labels = payload.get("labels") if isinstance(payload.get("labels"), dict) else {}
    annotations = payload.get("annotations") if isinstance(payload.get("annotations"), dict) else {}
    return AlertInput(
        name=str(payload.get("name") or payload.get("alertname") or labels.get("alertname") or "UnnamedAlert"),
        service=str(
            payload.get("service")
            or labels.get("service")
            or labels.get("job")
            or labels.get("instance")
            or "unknown",
        ),
        severity=str(payload.get("severity") or labels.get("severity") or "HIGH").upper(),
        description=str(
            payload.get("description")
            or payload.get("summary")
            or annotations.get("description")
            or annotations.get("summary")
            or "Live alert payload provided without description",
        ),
        source=str(payload.get("source") or labels.get("source") or "prometheus"),
        labels={str(key): str(value) for key, value in labels.items()},
        annotations={str(key): str(value) for key, value in annotations.items()},
    )


def _build_workflow_response(
    flow_id: str | None,
    alert_input: AlertInput,
    analysis: IncidentAnalysis,
    trace_id: str | None,
) -> dict[str, Any]:
    trace = trace_id or uuid4().hex
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()

    incident_id = f"INC-{uuid4().hex[:8].upper()}"
    alert_id = f"ALR-{uuid4().hex[:8].upper()}"
    correlation_id = f"COR-{uuid4().hex[:6].upper()}"
    recommendation_id = f"REC-{uuid4().hex[:8].upper()}"
    approval_id = f"APR-{uuid4().hex[:8].upper()}"
    action_id = f"ACT-{uuid4().hex[:8].upper()}"

    severity = alert_input.severity.upper()
    requires_approval = analysis.requires_approval if analysis.workflow == "auto_remediate_with_approval" else analysis.requires_approval

    alert = {
        "id": alert_id,
        "source": alert_input.source,
        "name": alert_input.name,
        "service": alert_input.service,
        "severity": severity,
        "description": alert_input.description,
        "labels": alert_input.labels,
        "annotations": alert_input.annotations,
        "trace_id": trace,
        "correlation_id": correlation_id,
        "deduplicated_count": 3 if severity == "CRITICAL" else 1,
        "created_at": timestamp,
    }

    incident = {
        "id": incident_id,
        "title": alert_input.name,
        "service": alert_input.service,
        "severity": severity,
        "status": "investigating",
        "trace_id": trace,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    decision = {
        "workflow": analysis.workflow,
        "next_action": analysis.next_action,
        "requires_approval": requires_approval,
        "downstream_agents": analysis.downstream_agents,
    }

    context = {
        "incident_id": incident_id,
        "deployment": alert_input.labels.get("deployment", alert_input.service),
        "runbook": analysis.runbook,
        "related_incidents": analysis.related_incidents,
        "dependency_services": analysis.dependency_services,
        "recent_changes": analysis.recent_changes,
        "metrics": {
            "saturation": analysis.saturation,
            "trend": analysis.trend,
        },
        "trace_id": trace,
    }

    recommendation = {
        "id": recommendation_id,
        "incident_id": incident_id,
        "root_cause": analysis.root_cause,
        "confidence": analysis.confidence,
        "impact": analysis.impact,
        "recommended_action": analysis.recommended_action,
        "severity": severity,
        "rationale": analysis.rationale,
        "commands": [],
        "risk": analysis.risk,
        "trace_id": trace,
    }

    approval = {
        "id": approval_id,
        "incident_id": incident_id,
        "recommendation_id": recommendation_id,
        "decision": "APPROVED" if not requires_approval else "PENDING",
        "approver": "kaiops-llm" if analysis.usage else "kaiops-demo",
        "channel": "web",
        "comment": analysis.recommended_action,
        "trace_id": trace,
        "decided_at": timestamp,
    }

    remediation_action = {
        "id": action_id,
        "approval_id": approval_id,
        "action_type": analysis.action_type,
        "target": analysis.target,
        "status": "completed" if not requires_approval else "pending_approval",
        "output": f"Executed {analysis.action_type} on {analysis.target}." if not requires_approval else "Awaiting approval before executing remediation.",
        "parameters": {
            "root_cause": analysis.root_cause,
            "impact": analysis.impact,
        },
        "trace_id": trace,
        "started_at": timestamp,
        "completed_at": timestamp,
    }

    closure_report = {
        "incident_id": incident_id,
        "health_restored": not requires_approval,
        "alerts_cleared": 1 if not requires_approval else 0,
        "knowledge_base_entry": analysis.knowledge_base_entry,
        "trace_id": trace,
        "validated_at": timestamp,
    }

    events = [
        {
            "sequence": 1,
            "agent": "Alert Intelligence Agent",
            "action": "Deduplicated, correlated, classified, and enriched alert",
            "input": {
                "flow_id": flow_id,
                "source": alert_input.source,
                "service": alert_input.service,
                "severity": severity,
            },
            "decision": f"Severity classified as {severity}; correlation ID {correlation_id}",
            "output": "Created incident and enriched alert event",
            "communicates_to": "Orchestrator Agent via enriched-alerts",
            "metrics": {
                "deduplicated_count": alert["deduplicated_count"],
                "metadata_fields": len(alert_input.labels) + len(alert_input.annotations),
            },
        },
        {
            "sequence": 2,
            "agent": "Orchestrator Agent",
            "action": "Selected incident workflow and downstream agents",
            "input": {
                "incident_id": incident_id,
                "service": alert_input.service,
                "severity": severity,
                "title": alert_input.name,
            },
            "decision": decision["workflow"],
            "output": f"Next action: {decision['next_action']}; approval required: {requires_approval}",
            "communicates_to": ", ".join(decision["downstream_agents"]),
            "metrics": {
                "downstream_agents": len(decision["downstream_agents"]),
                "requires_approval": requires_approval,
            },
        },
        {
            "sequence": 3,
            "agent": "Context Intelligence Agent",
            "action": "Collected operational context and RAG evidence",
            "input": {
                "incident_id": incident_id,
                "alert_service": alert_input.service,
                "deployment_label": context["deployment"],
            },
            "decision": f"Most relevant deployment: {context['deployment']}",
            "output": "Context with runbook, related incidents, dependencies, and changes",
            "communicates_to": "Resolution Intelligence Agent via context-events",
            "metrics": {
                "related_incidents": len(context["related_incidents"]),
                "dependency_services": len(context["dependency_services"]),
                "recent_changes": len(context["recent_changes"]),
                "runbook_found": bool(context["runbook"]),
            },
        },
        {
            "sequence": 4,
            "agent": "Resolution Intelligence Agent",
            "action": "Ran LangGraph RCA workflow with OpenAI",
            "input": {
                "incident_id": incident_id,
                "severity": severity,
                "deployment": context["deployment"],
                "related_incidents": len(context["related_incidents"]),
            },
            "decision": (
                f"Root cause: {recommendation['root_cause']}; "
                f"action: {recommendation['recommended_action']}"
            ),
            "output": "Recommendation with impact, rationale, commands, confidence, and risk",
            "communicates_to": "Human Approval Layer via resolution-events",
            "metrics": {
                "confidence": analysis.confidence,
                "commands": len(recommendation["commands"]),
                "risk": recommendation["risk"],
            },
            "llm_usage": analysis.usage or None,
        },
        {
            "sequence": 5,
            "agent": "Human Approval Layer",
            "action": "Reviewed recommendation for approval",
            "input": {
                "incident_id": incident_id,
                "recommendation_id": recommendation_id,
                "recommended_action": recommendation["recommended_action"],
                "channel": approval["channel"],
            },
            "decision": approval["decision"],
            "output": f"Approval {approval['decision']} via {approval['channel']}",
            "communicates_to": "Remediation Automation Engine via approval-events",
            "metrics": {"approval_required": requires_approval, "channel": approval["channel"]},
        },
        {
            "sequence": 6,
            "agent": "Remediation Automation Engine",
            "action": "Executed remediation strategy plugin"
            if not requires_approval
            else "Held remediation pending approval",
            "input": {
                "approval_id": approval_id,
                "comment": approval["comment"],
                "action_type": remediation_action["action_type"],
                "target": remediation_action["target"],
            },
            "decision": f"Selected plugin action {remediation_action['action_type']}",
            "output": remediation_action["output"],
            "communicates_to": "Closure & Validation via remediation-events",
            "metrics": {
                "status": remediation_action["status"],
                "target": remediation_action["target"],
            },
        },
        {
            "sequence": 7,
            "agent": "Closure & Validation",
            "action": "Validated health and generated closure report",
            "input": {
                "remediation_action_id": action_id,
                "status": remediation_action["status"],
                "output": remediation_action["output"],
            },
            "decision": "Health restored" if closure_report["health_restored"] else "Awaiting approval",
            "output": closure_report["knowledge_base_entry"],
            "communicates_to": "Knowledge Base and audit log",
            "metrics": {
                "alerts_cleared": closure_report["alerts_cleared"],
                "health_restored": closure_report["health_restored"],
            },
        },
    ]

    metrics = {
        "alerts_processed": 1,
        "deduplicated_count": alert["deduplicated_count"],
        "severity": severity,
        "related_incidents": len(context["related_incidents"]),
        "dependency_services": len(context["dependency_services"]),
        "recent_changes": len(context["recent_changes"]),
        "recommendation_confidence": analysis.confidence,
        "agent_handoffs": 6,
        "approval_required": requires_approval,
        "remediation_status": remediation_action["status"],
        "health_restored": closure_report["health_restored"],
        "alerts_cleared": closure_report["alerts_cleared"],
    }

    finops_totals = {
        "input_tokens": int(analysis.usage.get("prompt_tokens", 0) or 0),
        "output_tokens": int(analysis.usage.get("completion_tokens", 0) or 0),
        "total_tokens": int(analysis.usage.get("total_tokens", 0) or 0),
        "total_cost_usd": _estimate_cost(analysis.usage),
        "calls": 1 if analysis.usage else 0,
        "failed_calls": 0,
    }
    finops = {
        "totals": finops_totals,
        "by_provider": (
            [
                {
                    "provider": "openai",
                    "model": analysis.usage.get("model"),
                    "input_tokens": finops_totals["input_tokens"],
                    "output_tokens": finops_totals["output_tokens"],
                    "total_tokens": finops_totals["total_tokens"],
                    "estimated_cost_usd": finops_totals["total_cost_usd"],
                }
            ]
            if analysis.usage
            else []
        ),
        "errors": [],
        "note": (
            "OpenAI chat completion drove this analysis."
            if analysis.usage
            else "LLM not configured; analysis derived from fallback heuristics."
        ),
    }

    return {
        "mode": "llm" if analysis.usage else "fallback",
        "scenario": {
            "id": flow_id or "live-alert",
            "title": alert_input.name,
            "service": alert_input.service,
            "severity": severity,
            "recommended_action": analysis.recommended_action,
            "source": alert_input.source,
            "description": alert_input.description,
        },
        "alert": alert,
        "incident": incident,
        "decision": decision,
        "context": context,
        "recommendation": recommendation,
        "approval": approval,
        "remediation_action": remediation_action,
        "closure_report": closure_report,
        "metrics": metrics,
        "finops": finops,
        "events": events,
        "next_step": closure_report["knowledge_base_entry"],
        "trace_id": trace,
        "generated_at": timestamp,
    }


def _estimate_cost(usage: dict[str, Any]) -> float:
    if not usage:
        return 0.0
    prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
    completion_tokens = int(usage.get("completion_tokens", 0) or 0)
    # rough gpt-4o-mini pricing: $0.15 / 1M input, $0.60 / 1M output
    input_cost = (prompt_tokens / 1_000_000) * 0.15
    output_cost = (completion_tokens / 1_000_000) * 0.60
    return round(input_cost + output_cost, 6)


def _fallback_analysis(alert: AlertInput, reason: str) -> IncidentAnalysis:
    severity = alert.severity.upper()
    risk = "high" if severity == "CRITICAL" else ("medium" if severity == "HIGH" else "low")
    confidence = 0.7 if severity == "CRITICAL" else 0.62
    return IncidentAnalysis(
        root_cause="LLM analysis unavailable; manual triage required.",
        impact=f"Potential {severity.lower()} impact for {alert.service}.",
        recommended_action="Investigate issue",
        action_type="other",
        target=alert.service,
        rationale=f"Fallback analysis generated because: {reason}",
        risk=risk,
        confidence=confidence,
        runbook="runbooks/general-triage.md",
        related_incidents=[],
        dependency_services=[],
        recent_changes=[],
        workflow="auto_remediate_with_approval",
        next_action="Triage with on-call engineer",
        requires_approval=True,
        downstream_agents=["context-agent", "resolution-agent", "remediation-engine"],
        saturation="elevated",
        trend="degrading",
        knowledge_base_entry=f"Manual triage required for {alert.service}.",
        usage={},
    )


class SampleFlowService:
    def __init__(self, analyst: IncidentAnalyst | None = None) -> None:
        self.analyst = analyst or IncidentAnalyst()

    def list_flows(self) -> list[dict[str, str]]:
        return list_flows()

    async def run_workflow(
        self,
        flow_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_flow_id, alert_input = _alert_from_catalog(flow_id or DEFAULT_FLOW_ID)
        analysis = await self._analyze(alert_input)
        return _build_workflow_response(resolved_flow_id, alert_input, analysis, trace_id)

    async def run_workflow_from_alert(
        self,
        alert_payload: dict[str, Any],
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        alert_input = _normalize_alert_input(alert_payload)
        analysis = await self._analyze(alert_input)
        return _build_workflow_response(None, alert_input, analysis, trace_id)

    async def _analyze(self, alert_input: AlertInput) -> IncidentAnalysis:
        if not self.analyst.is_enabled:
            return _fallback_analysis(alert_input, "OPENAI_API_KEY not configured")
        try:
            return await self.analyst.analyze(alert_input)
        except LLMUnavailableError as exc:
            logger.warning("LLM analysis failed: %s", exc)
            return _fallback_analysis(alert_input, str(exc))
