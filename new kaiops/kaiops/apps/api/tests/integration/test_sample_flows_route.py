from fastapi.testclient import TestClient

from app.main import app


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


def test_sample_flow_workflow_returns_full_payload():
    with TestClient(app) as client:
        response = client.post("/api/v1/sample/payment-latency/workflow")

    assert response.status_code == 200
    body = response.json()
    assert body["scenario"]["id"] == "payment-latency"
    assert body["scenario"]["title"]
    assert body["alert"]["service"] == "payments"
    assert body["recommendation"]["recommended_action"] == "Rollback deployment"
    assert body["closure_report"]["health_restored"] is True
    assert [event["sequence"] for event in body["events"]] == [1, 2, 3, 4, 5, 6, 7]
    assert body["metrics"]["agent_handoffs"] == 6


def test_sample_flow_workflow_unknown_flow_returns_404():
    with TestClient(app) as client:
        response = client.post("/api/v1/sample/not-a-real-flow/workflow")
    assert response.status_code == 404
