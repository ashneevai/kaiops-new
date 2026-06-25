from hashlib import sha256


SOURCE_MAP = {
    "prometheus": "prometheus",
    "grafana": "grafana",
    "datadog": "datadog",
    "dynatrace": "dynatrace",
    "newrelic": "newrelic",
    "cloudwatch": "cloudwatch",
    "azuremonitor": "azuremonitor",
    "elastic": "elastic",
    "custom": "custom",
}


class AlertIngestionService:
    def normalize(self, source: str, payload: dict) -> dict:
        source_name = SOURCE_MAP.get(source.lower(), "custom")
        title = payload.get("title") or payload.get("alert") or "Unknown alert"
        severity = (payload.get("severity") or "warning").lower()
        service_name = payload.get("service") or payload.get("service_name")
        external_id = str(payload.get("id") or payload.get("fingerprint") or title)

        dedupe_key = sha256(f"{source_name}:{external_id}:{service_name}".encode("utf-8")).hexdigest()
        correlation_key = sha256(f"{service_name}:{severity}".encode("utf-8")).hexdigest()

        score_map = {"critical": 100, "high": 80, "warning": 60, "info": 30}
        severity_score = score_map.get(severity, 50)

        return {
            "source": source_name,
            "external_id": external_id,
            "title": title,
            "description": payload.get("description"),
            "severity": severity,
            "status": "open",
            "service_name": service_name,
            "dedupe_key": dedupe_key,
            "correlation_key": correlation_key,
            "severity_score": severity_score,
            "normalized_payload": payload,
        }
