from fastapi.testclient import TestClient

from app.main import app
from services.llm.incident_analyst import IncidentAnalysis


def _mock_analysis() -> IncidentAnalysis:
    return IncidentAnalysis(
        root_cause="Recent deployment regressed payment latency.",
        impact="Customer checkout slow path elevated p95 latency.",
        recommended_action="Rollback deployment",
        action_type="rollback",
        target="payments-api",
        rationale="Latency spike began immediately after the new deployment.",
        risk="high",
        confidence=0.84,
        runbook="runbooks/payments-rollback.md",
        related_incidents=["INC-8842", "INC-7211"],
        dependency_services=["checkout", "fraud", "orders-db"],
        recent_changes=["CHG-90211 Deployment 2.5"],
        workflow="auto_remediate_with_approval",
        next_action="Coordinate with payments-sre to confirm rollback",
        requires_approval=True,
        downstream_agents=["context-agent", "resolution-agent", "remediation-engine"],
        saturation="elevated",
        trend="degrading",
        knowledge_base_entry="Payment latency restored after rollback validation.",
        usage={"model": "gpt-test", "prompt_tokens": 120, "completion_tokens": 80, "total_tokens": 200},
    )


def test_sample_flows_list_is_public_and_returns_catalog():
    with TestClient(app) as client:
        response = client.get("/api/v1/sample/flows")

    assert response.status_code == 200
    body = response.json()
    assert "flows" in body
    flow_ids = [flow["id"] for flow in body["flows"]]
    assert "payment-latency" in flow_ids
    payment = next(flow for flow in body["flows"] if flow["id"] == "payment-latency")
    assert payment["severity"] == "CRITICAL"
    assert payment["service"] == "payments"


def test_sample_flow_workflow_uses_llm_when_available(monkeypatch):
    async def fake_analyze(self, alert):
        return _mock_analysis()

    monkeypatch.setattr("services.llm.incident_analyst.IncidentAnalyst.is_enabled", property(lambda self: True))
    monkeypatch.setattr("services.llm.incident_analyst.IncidentAnalyst.analyze", fake_analyze)

    with TestClient(app) as client:
        response = client.post("/api/v1/sample/payment-latency/workflow")

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "llm"
    assert body["recommendation"]["root_cause"].startswith("Recent deployment")
    assert body["recommendation"]["recommended_action"] == "Rollback deployment"
    assert body["finops"]["totals"]["total_tokens"] == 200
    assert [event["sequence"] for event in body["events"]] == [1, 2, 3, 4, 5, 6, 7]


def test_sample_flow_workflow_falls_back_without_llm(monkeypatch):
    monkeypatch.setattr("services.llm.incident_analyst.IncidentAnalyst.is_enabled", property(lambda self: False))

    with TestClient(app) as client:
        response = client.post("/api/v1/sample/payment-latency/workflow")

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "fallback"
    assert body["recommendation"]["recommended_action"] == "Investigate issue"
    assert body["finops"]["totals"]["calls"] == 0


def test_sample_flow_workflow_unknown_flow_returns_404():
    with TestClient(app) as client:
        response = client.post("/api/v1/sample/not-a-real-flow/workflow")
    assert response.status_code == 404


def test_from_alert_workflow_uses_alert_payload(monkeypatch):
    async def fake_analyze(self, alert):
        analysis = _mock_analysis()
        analysis.target = alert.service
        return analysis

    monkeypatch.setattr("services.llm.incident_analyst.IncidentAnalyst.is_enabled", property(lambda self: True))
    monkeypatch.setattr("services.llm.incident_analyst.IncidentAnalyst.analyze", fake_analyze)

    payload = {
        "name": "OrdersLatencyHigh",
        "service": "orders-api",
        "severity": "HIGH",
        "description": "p95 latency elevated for orders read path",
        "labels": {"deployment": "orders-api", "team": "orders-sre"},
        "annotations": {"summary": "Orders latency"},
        "source": "prometheus",
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/sample/from-alert/workflow", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["scenario"]["id"] == "live-alert"
    assert body["alert"]["service"] == "orders-api"
    assert body["remediation_action"]["target"] == "orders-api"
