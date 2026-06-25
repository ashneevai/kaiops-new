from dataclasses import dataclass


@dataclass(frozen=True)
class TopicConfig:
    name: str
    dlq: str


TOPICS: dict[str, TopicConfig] = {
    "alerts": TopicConfig(name="alerts", dlq="alerts.dlq"),
    "incidents": TopicConfig(name="incidents", dlq="incidents.dlq"),
    "workflows": TopicConfig(name="workflows", dlq="workflows.dlq"),
    "agent-events": TopicConfig(name="agent-events", dlq="agent-events.dlq"),
    "approvals": TopicConfig(name="approvals", dlq="approvals.dlq"),
    "automation": TopicConfig(name="automation", dlq="automation.dlq"),
    "audit": TopicConfig(name="audit", dlq="audit.dlq"),
}
