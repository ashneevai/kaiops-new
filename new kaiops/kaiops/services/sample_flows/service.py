from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from services.sample_flows.data import SCENARIOS

SEVERITY_BASE_CONFIDENCE = {
    "CRITICAL": 0.83,
    "HIGH": 0.76,
    "WARNING": 0.68,
    "INFO": 0.6,
}

DEFAULT_FLOW_ID = "payment-latency"


def _confidence_for(scenario: dict[str, Any]) -> float:
    severity = str(scenario.get("severity", "HIGH")).upper()
    base = SEVERITY_BASE_CONFIDENCE.get(severity, 0.7)
    digest = hashlib.sha256(scenario["title"].encode("utf-8")).digest()
    jitter = (digest[0] / 255) * 0.12
    return round(min(0.96, base + jitter), 2)


def list_flows() -> list[dict[str, str]]:
    rows = [
        {
            "id": scenario_id,
            "alert_id": scenario.get("alert_id", scenario_id.upper()),
            "alert_name": scenario.get("alert_name", scenario["title"]),
            "alert_type": scenario.get("alert_type", scenario.get("source", "")),
            "title": scenario["title"],
            "service": scenario["service"],
            "severity": scenario["severity"],
            "recommended_action": scenario["recommended_action"],
            "description": scenario["description"],
        }
        for scenario_id, scenario in SCENARIOS.items()
    ]
    return sorted(rows, key=lambda item: (item["service"].lower(), item["title"].lower()))


def run_workflow(flow_id: str | None = None, trace_id: str | None = None) -> dict[str, Any]:
    resolved_flow_id = flow_id if flow_id and flow_id in SCENARIOS else DEFAULT_FLOW_ID
    scenario = SCENARIOS[resolved_flow_id]
    trace = trace_id or uuid4().hex
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()
    confidence = _confidence_for(scenario)
    severity = str(scenario["severity"]).upper()
    requires_approval = severity in {"CRITICAL", "HIGH"}

    incident_id = f"INC-{uuid4().hex[:8].upper()}"
    alert_id = f"ALR-{uuid4().hex[:8].upper()}"
    correlation_id = f"COR-{uuid4().hex[:6].upper()}"
    recommendation_id = f"REC-{uuid4().hex[:8].upper()}"
    approval_id = f"APR-{uuid4().hex[:8].upper()}"
    action_id = f"ACT-{uuid4().hex[:8].upper()}"

    alert = {
        "id": alert_id,
        "source": scenario["source"],
        "name": scenario["name"],
        "service": scenario["service"],
        "severity": severity,
        "description": scenario["description"],
        "labels": scenario["labels"],
        "annotations": scenario["annotations"],
        "trace_id": trace,
        "correlation_id": correlation_id,
        "deduplicated_count": 3 if severity == "CRITICAL" else 1,
        "created_at": timestamp,
    }

    incident = {
        "id": incident_id,
        "title": scenario["title"],
        "service": scenario["service"],
        "severity": severity,
        "status": "investigating",
        "trace_id": trace,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    decision = {
        "workflow": "auto_remediate_with_approval" if requires_approval else "auto_remediate",
        "next_action": scenario["recommended_action"],
        "requires_approval": requires_approval,
        "downstream_agents": list(scenario["downstream_agents"]),
    }

    context = {
        "incident_id": incident_id,
        "deployment": scenario["labels"].get("deployment"),
        "runbook": scenario["runbook"],
        "related_incidents": list(scenario["related_incidents"]),
        "dependency_services": list(scenario["dependency_services"]),
        "recent_changes": list(scenario["recent_changes"]),
        "metrics": {
            "saturation": "elevated" if severity == "CRITICAL" else "warning",
            "trend": "increasing",
        },
        "trace_id": trace,
    }

    recommendation = {
        "id": recommendation_id,
        "incident_id": incident_id,
        "root_cause": scenario["root_cause"],
        "confidence": confidence,
        "impact": scenario["impact"],
        "recommended_action": scenario["recommended_action"],
        "severity": severity,
        "rationale": (
            f"Scenario evidence links {scenario['root_cause']} to {scenario['impact']}; "
            f"recommended action is {scenario['recommended_action']}."
        ),
        "commands": [],
        "risk": "high" if severity == "CRITICAL" else "medium",
        "trace_id": trace,
    }

    approval = {
        "id": approval_id,
        "incident_id": incident_id,
        "recommendation_id": recommendation_id,
        "decision": "APPROVED",
        "approver": "kaiops-demo",
        "channel": "web",
        "comment": scenario["remediation_comment"],
        "trace_id": trace,
        "decided_at": timestamp,
    }

    remediation_action = {
        "id": action_id,
        "approval_id": approval_id,
        "action_type": scenario["action_type"],
        "target": scenario["target"],
        "status": "completed",
        "output": f"Executed {scenario['action_type']} on {scenario['target']} as part of demo flow",
        "parameters": {
            "root_cause": scenario["root_cause"],
            "impact": scenario["impact"],
        },
        "trace_id": trace,
        "started_at": timestamp,
        "completed_at": timestamp,
    }

    closure_report = {
        "incident_id": incident_id,
        "health_restored": True,
        "alerts_cleared": 1,
        "knowledge_base_entry": (
            f"Closed {incident_id} via {scenario['recommended_action'].lower()} on {scenario['target']}."
        ),
        "trace_id": trace,
        "validated_at": timestamp,
    }

    events = [
        {
            "sequence": 1,
            "agent": "Alert Intelligence Agent",
            "action": "Deduplicated, correlated, classified, and enriched alert",
            "input": {
                "flow_id": resolved_flow_id,
                "source": alert["source"],
                "service": alert["service"],
                "severity": severity,
            },
            "decision": f"Severity classified as {severity}; correlation ID {correlation_id}",
            "output": "Created incident and enriched alert event",
            "communicates_to": "Orchestrator Agent via enriched-alerts",
            "metrics": {
                "deduplicated_count": alert["deduplicated_count"],
                "metadata_fields": len(alert["labels"]) + len(alert["annotations"]),
            },
        },
        {
            "sequence": 2,
            "agent": "Orchestrator Agent",
            "action": "Selected incident workflow and downstream agents",
            "input": {
                "incident_id": incident_id,
                "service": scenario["service"],
                "severity": severity,
                "title": scenario["title"],
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
                "alert_service": scenario["service"],
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
            "action": "Ran LangGraph RCA workflow",
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
                "confidence": confidence,
                "commands": len(recommendation["commands"]),
                "risk": recommendation["risk"],
            },
        },
        {
            "sequence": 5,
            "agent": "Human Approval Layer",
            "action": "Auto-approved demo recommendation",
            "input": {
                "incident_id": incident_id,
                "recommendation_id": recommendation_id,
                "recommended_action": recommendation["recommended_action"],
                "channel": approval["channel"],
            },
            "decision": approval["decision"],
            "output": f"Approved by {approval['approver']} on {approval['channel']}",
            "communicates_to": "Remediation Automation Engine via approval-events",
            "metrics": {"approval_required": requires_approval, "channel": approval["channel"]},
        },
        {
            "sequence": 6,
            "agent": "Remediation Automation Engine",
            "action": "Executed remediation strategy plugin",
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
            "decision": "Health restored" if closure_report["health_restored"] else "Health not restored",
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
        "recommendation_confidence": confidence,
        "agent_handoffs": 6,
        "approval_required": requires_approval,
        "remediation_status": remediation_action["status"],
        "health_restored": closure_report["health_restored"],
        "alerts_cleared": closure_report["alerts_cleared"],
    }

    finops = {
        "totals": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "calls": 0,
            "failed_calls": 0,
        },
        "by_provider": [],
        "errors": [],
        "note": "Sample flow executed locally without LLM provider calls.",
    }

    return {
        "mode": "local-no-kafka",
        "scenario": {
            "id": resolved_flow_id,
            "title": scenario["title"],
            "service": scenario["service"],
            "severity": severity,
            "recommended_action": scenario["recommended_action"],
            "source": scenario["source"],
            "description": scenario["description"],
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
        "next_step": "Incident closed in local demo. Review closure report and lessons learned.",
        "trace_id": trace,
        "generated_at": timestamp,
    }


class SampleFlowService:
    def list_flows(self) -> list[dict[str, str]]:
        return list_flows()

    def run_workflow(self, flow_id: str | None = None, trace_id: str | None = None) -> dict[str, Any]:
        return run_workflow(flow_id=flow_id, trace_id=trace_id)
