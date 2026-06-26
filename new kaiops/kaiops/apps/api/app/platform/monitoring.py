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
