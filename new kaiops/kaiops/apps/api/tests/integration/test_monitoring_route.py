from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.platform.monitoring import (
    MonitoringAlert,
    MonitoringAlertsResponse,
    MonitoringOverviewResponse,
    MonitoringSummary,
    MonitoringTarget,
)


def test_monitoring_overview_is_public_and_returns_prometheus_details(monkeypatch):
    async def fake_get_overview(self):
        return MonitoringOverviewResponse(
            connected=True,
            prometheus_url="http://localhost:9090",
            generated_at=datetime(2026, 6, 26, tzinfo=timezone.utc),
            summary=MonitoringSummary(
                total_targets=2,
                healthy_targets=2,
                unhealthy_targets=0,
                monitored_jobs=["kaiops-api", "prometheus"],
                self_monitoring_enabled=True,
            ),
            targets=[
                MonitoringTarget(
                    job="prometheus",
                    endpoint="localhost:9090",
                    health="up",
                    labels={"job": "prometheus", "instance": "localhost:9090"},
                    scrape_url="http://localhost:9090/metrics",
                ),
                MonitoringTarget(
                    job="kaiops-api",
                    endpoint="host.docker.internal:8000",
                    health="up",
                    labels={"job": "kaiops-api", "instance": "host.docker.internal:8000"},
                    scrape_url="http://host.docker.internal:8000/metrics",
                ),
            ],
        )

    monkeypatch.setattr("app.api.v1.monitoring.PrometheusMonitoringClient.get_overview", fake_get_overview)

    with TestClient(app) as client:
        response = client.get("/api/v1/monitoring/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["connected"] is True
    assert body["summary"]["self_monitoring_enabled"] is True
    assert body["summary"]["healthy_targets"] == 2
    assert [target["job"] for target in body["targets"]] == ["prometheus", "kaiops-api"]


def test_monitoring_alerts_is_public_and_returns_prometheus_alerts(monkeypatch):
    async def fake_get_alerts(self):
        return MonitoringAlertsResponse(
            connected=True,
            prometheus_url="http://localhost:9090",
            generated_at=datetime(2026, 6, 26, tzinfo=timezone.utc),
            total_alerts=2,
            firing_alerts=1,
            pending_alerts=1,
            alerts=[
                MonitoringAlert(
                    name="KaiOpsApiScrapeSlow",
                    state="firing",
                    severity="warning",
                    service="kaiops-api",
                    summary="API scrape duration is above threshold",
                    labels={"alertname": "KaiOpsApiScrapeSlow", "service": "kaiops-api", "severity": "warning"},
                ),
                MonitoringAlert(
                    name="KaiOpsPrometheusScrapeSlow",
                    state="pending",
                    severity="warning",
                    service="prometheus",
                    summary="Prometheus self-scrape duration is above threshold",
                    labels={"alertname": "KaiOpsPrometheusScrapeSlow", "service": "prometheus", "severity": "warning"},
                ),
            ],
        )

    monkeypatch.setattr("app.api.v1.monitoring.PrometheusMonitoringClient.get_alerts", fake_get_alerts)

    with TestClient(app) as client:
        response = client.get("/api/v1/monitoring/alerts")

    assert response.status_code == 200
    body = response.json()
    assert body["connected"] is True
    assert body["total_alerts"] == 2
    assert body["firing_alerts"] == 1
    assert body["pending_alerts"] == 1
    assert [alert["name"] for alert in body["alerts"]] == ["KaiOpsApiScrapeSlow", "KaiOpsPrometheusScrapeSlow"]
