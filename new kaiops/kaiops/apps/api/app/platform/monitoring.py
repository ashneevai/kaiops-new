from datetime import datetime, timezone
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings


class MonitoringTarget(BaseModel):
    job: str
    endpoint: str
    health: str
    labels: dict[str, str] = Field(default_factory=dict)
    last_error: str | None = None
    last_scrape: datetime | None = None
    last_scrape_duration_seconds: float | None = None
    scrape_url: str | None = None


class MonitoringSummary(BaseModel):
    total_targets: int = 0
    healthy_targets: int = 0
    unhealthy_targets: int = 0
    monitored_jobs: list[str] = Field(default_factory=list)
    self_monitoring_enabled: bool = False


class MonitoringOverviewResponse(BaseModel):
    connected: bool
    prometheus_url: str
    generated_at: datetime
    summary: MonitoringSummary
    targets: list[MonitoringTarget] = Field(default_factory=list)
    error: str | None = None


class MonitoringAlert(BaseModel):
    name: str
    state: str
    severity: str
    service: str
    summary: str
    description: str | None = None
    active_at: datetime | None = None
    value: str | None = None
    source_url: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class MonitoringAlertsResponse(BaseModel):
    connected: bool
    prometheus_url: str
    generated_at: datetime
    total_alerts: int = 0
    firing_alerts: int = 0
    pending_alerts: int = 0
    inactive_alerts: int = 0
    alerts: list[MonitoringAlert] = Field(default_factory=list)
    error: str | None = None


class PrometheusMonitoringClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.prometheus_base_url).rstrip("/")

    async def get_overview(self) -> MonitoringOverviewResponse:
        generated_at = datetime.now(timezone.utc)

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
                response = await client.get("/api/v1/targets")
                response.raise_for_status()
            payload = response.json().get("data", {})
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            return MonitoringOverviewResponse(
                connected=False,
                prometheus_url=self.base_url,
                generated_at=generated_at,
                summary=MonitoringSummary(),
                error=str(exc),
            )

        targets = [self._map_target(target_payload) for target_payload in payload.get("activeTargets", [])]
        targets.sort(key=lambda target: (target.job, target.endpoint))

        healthy_targets = sum(target.health == "up" for target in targets)
        monitored_jobs = sorted({target.job for target in targets})

        return MonitoringOverviewResponse(
            connected=True,
            prometheus_url=self.base_url,
            generated_at=generated_at,
            summary=MonitoringSummary(
                total_targets=len(targets),
                healthy_targets=healthy_targets,
                unhealthy_targets=len(targets) - healthy_targets,
                monitored_jobs=monitored_jobs,
                self_monitoring_enabled=any(target.job == "prometheus" for target in targets),
            ),
            targets=targets,
        )

    async def get_alerts(self) -> MonitoringAlertsResponse:
        generated_at = datetime.now(timezone.utc)

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
                alerts_response = await client.get("/api/v1/alerts")
                alerts_response.raise_for_status()
                rules_response = await client.get("/api/v1/rules")
                rules_response.raise_for_status()
            active_payload = alerts_response.json().get("data", {})
            rules_payload = rules_response.json().get("data", {})
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            return MonitoringAlertsResponse(
                connected=False,
                prometheus_url=self.base_url,
                generated_at=generated_at,
                error=str(exc),
            )

        active_alerts = [self._map_alert(alert_payload) for alert_payload in active_payload.get("alerts", [])]
        alert_index = {self._alert_key(alert): alert for alert in active_alerts}

        rules_alerts: list[MonitoringAlert] = []
        for group in rules_payload.get("groups", []):
            for rule in group.get("rules", []):
                if rule.get("type") != "alerting":
                    continue
                mapped = self._map_rule_alert(rule)
                key = self._alert_key(mapped)
                rules_alerts.append(alert_index.get(key, mapped))

        alerts = rules_alerts if rules_alerts else active_alerts
        alerts.sort(
            key=lambda alert: (
                0 if alert.state == "firing" else 1,
                1 if alert.state == "inactive" else 0,
                -(alert.active_at.timestamp() if alert.active_at else 0),
                alert.name,
                alert.service,
            )
        )

        firing_alerts = sum(alert.state == "firing" for alert in alerts)
        pending_alerts = sum(alert.state == "pending" for alert in alerts)
        inactive_alerts = sum(alert.state == "inactive" for alert in alerts)

        return MonitoringAlertsResponse(
            connected=True,
            prometheus_url=self.base_url,
            generated_at=generated_at,
            total_alerts=len(alerts),
            firing_alerts=firing_alerts,
            pending_alerts=pending_alerts,
            inactive_alerts=inactive_alerts,
            alerts=alerts,
        )

    @staticmethod
    def _alert_key(alert: MonitoringAlert) -> str:
        return f"{alert.name}::{alert.service}"

    def _map_target(self, target_payload: dict[str, Any]) -> MonitoringTarget:
        labels = self._string_dict(target_payload.get("labels"))
        discovered_labels = self._string_dict(target_payload.get("discoveredLabels"))

        endpoint = (
            labels.get("instance")
            or discovered_labels.get("__address__")
            or target_payload.get("scrapeUrl")
            or "unknown"
        )

        return MonitoringTarget(
            job=labels.get("job", "unknown"),
            endpoint=endpoint,
            health=str(target_payload.get("health", "unknown")).lower(),
            labels=labels,
            last_error=target_payload.get("lastError") or None,
            last_scrape=self._parse_datetime(target_payload.get("lastScrape")),
            last_scrape_duration_seconds=self._parse_float(target_payload.get("lastScrapeDuration")),
            scrape_url=target_payload.get("scrapeUrl"),
        )

    def _map_alert(self, alert_payload: dict[str, Any]) -> MonitoringAlert:
        labels = self._string_dict(alert_payload.get("labels"))
        annotations = self._string_dict(alert_payload.get("annotations"))

        name = labels.get("alertname", "UnnamedAlert")
        summary = annotations.get("summary") or annotations.get("message") or name

        return MonitoringAlert(
            name=name,
            state=str(alert_payload.get("state", "unknown")).lower(),
            severity=labels.get("severity", "unknown"),
            service=labels.get("service") or labels.get("job") or labels.get("instance") or "unknown",
            summary=summary,
            description=annotations.get("description"),
            active_at=self._parse_datetime(alert_payload.get("activeAt")),
            value=alert_payload.get("value") if isinstance(alert_payload.get("value"), str) else None,
            source_url=alert_payload.get("generatorURL") if isinstance(alert_payload.get("generatorURL"), str) else None,
            labels=labels,
            annotations=annotations,
        )

    def _map_rule_alert(self, rule_payload: dict[str, Any]) -> MonitoringAlert:
        labels = self._string_dict(rule_payload.get("labels"))
        annotations = self._string_dict(rule_payload.get("annotations"))
        alert_entries = rule_payload.get("alerts") if isinstance(rule_payload.get("alerts"), list) else []
        first_alert = alert_entries[0] if alert_entries else {}

        name = str(rule_payload.get("name") or labels.get("alertname") or "UnnamedAlert")
        summary = annotations.get("summary") or annotations.get("message") or name

        return MonitoringAlert(
            name=name,
            state=str(rule_payload.get("state", "inactive")).lower(),
            severity=labels.get("severity", "unknown"),
            service=labels.get("service") or labels.get("job") or labels.get("instance") or "unknown",
            summary=summary,
            description=annotations.get("description"),
            active_at=self._parse_datetime(first_alert.get("activeAt")),
            value=first_alert.get("value") if isinstance(first_alert.get("value"), str) else None,
            source_url=first_alert.get("generatorURL") if isinstance(first_alert.get("generatorURL"), str) else None,
            labels=labels,
            annotations=annotations,
        )

    @staticmethod
    def _string_dict(value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        return {str(key): str(item) for key, item in value.items()}

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _parse_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
