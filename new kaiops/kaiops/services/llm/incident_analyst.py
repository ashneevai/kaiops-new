from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMUnavailableError(RuntimeError):
    """Raised when the LLM provider cannot be reached or is not configured."""


@dataclass(slots=True)
class AlertInput:
    name: str
    service: str
    severity: str
    description: str
    source: str = "unknown"
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class IncidentAnalysis:
    root_cause: str
    impact: str
    recommended_action: str
    action_type: str
    target: str
    rationale: str
    risk: str
    confidence: float
    runbook: str
    related_incidents: list[str]
    dependency_services: list[str]
    recent_changes: list[str]
    workflow: str
    next_action: str
    requires_approval: bool
    downstream_agents: list[str]
    saturation: str
    trend: str
    knowledge_base_entry: str
    usage: dict[str, Any] = field(default_factory=dict)


SYSTEM_PROMPT = (
    "You are KaiOps Incident Intelligence, an autonomous SRE/AIOps assistant. "
    "Given a monitoring alert, you must produce a structured incident analysis. "
    "Be concise, operationally precise, and grounded in the alert content provided. "
    "Never invent unrealistic specifics; if a value is unknown, return a sensible placeholder."
)


JSON_SCHEMA_HINT = {
    "root_cause": "Short single-line root cause hypothesis.",
    "impact": "Short single-line impact description.",
    "recommended_action": "Short remediation action sentence (max 8 words).",
    "action_type": "One of: rollback | restart | scale | cache_evict | db_failover | terraform_rollback | api_execution | restart_service | failover | other.",
    "target": "Logical target system or component for the action (e.g. service or deployment name).",
    "rationale": "1-2 sentences explaining the reasoning that links root cause to recommended action.",
    "risk": "One of: low | medium | high.",
    "confidence": "Float between 0.5 and 0.95 indicating recommendation confidence.",
    "runbook": "Relative runbook path under runbooks/.",
    "related_incidents": "List of up to 3 likely related incident IDs.",
    "dependency_services": "List of up to 5 affected dependency services.",
    "recent_changes": "List of up to 3 likely recent changes that could have caused the issue.",
    "workflow": "One of: auto_remediate | auto_remediate_with_approval | escalate_only.",
    "next_action": "Short imperative next operational step.",
    "requires_approval": "Boolean indicating if human approval is required before remediation.",
    "downstream_agents": "List of downstream agent identifiers among: context-agent, resolution-agent, remediation-engine, closure-validation.",
    "saturation": "One of: nominal | elevated | warning | critical.",
    "trend": "One of: improving | steady | increasing | degrading.",
    "knowledge_base_entry": "Single-line KB entry summarising the closure note.",
}


def _user_prompt(alert: AlertInput) -> str:
    return (
        "Alert payload:\n"
        f"  Name: {alert.name}\n"
        f"  Service: {alert.service}\n"
        f"  Severity: {alert.severity}\n"
        f"  Source: {alert.source}\n"
        f"  Description: {alert.description}\n"
        f"  Labels: {json.dumps(alert.labels, sort_keys=True)}\n"
        f"  Annotations: {json.dumps(alert.annotations, sort_keys=True)}\n\n"
        "Respond with a single JSON object that conforms to this field hint:\n"
        f"{json.dumps(JSON_SCHEMA_HINT, indent=2)}\n"
    )


class IncidentAnalyst:
    """Calls OpenAI Chat Completions to derive an incident analysis from an alert."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_chat_model

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)

    async def analyze(self, alert: AlertInput) -> IncidentAnalysis:
        if not self.is_enabled:
            raise LLMUnavailableError("OPENAI_API_KEY is not configured for the API")

        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise LLMUnavailableError("openai package is not installed") from exc

        client = AsyncOpenAI(api_key=self.api_key, timeout=settings.openai_request_timeout_seconds)

        try:
            response = await client.chat.completions.create(
                model=self.model,
                temperature=settings.llm_temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _user_prompt(alert)},
                ],
            )
        except Exception as exc:
            logger.warning("LLM call failed: %s", exc)
            raise LLMUnavailableError(str(exc)) from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LLMUnavailableError("LLM returned empty content")

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMUnavailableError(f"LLM response was not valid JSON: {exc}") from exc

        usage_payload: dict[str, Any] = {}
        if response.usage is not None:
            usage_payload = {
                "model": response.model,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return _coerce_analysis(payload, usage_payload, fallback_target=alert.service)


def _ensure_list(value: Any, max_items: int) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            cleaned.append(text)
        if len(cleaned) >= max_items:
            break
    return cleaned


def _ensure_float(value: Any, default: float) -> float:
    try:
        if value is None:
            return default
        result = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.5, min(0.95, result))


def _ensure_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1"}
    return default


def _ensure_str(value: Any, default: str, max_length: int = 200) -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    return text[:max_length]


def _coerce_analysis(payload: dict[str, Any], usage: dict[str, Any], fallback_target: str) -> IncidentAnalysis:
    return IncidentAnalysis(
        root_cause=_ensure_str(payload.get("root_cause"), default="Unknown root cause"),
        impact=_ensure_str(payload.get("impact"), default="Service impact under investigation"),
        recommended_action=_ensure_str(payload.get("recommended_action"), default="Investigate issue"),
        action_type=_ensure_str(payload.get("action_type"), default="other", max_length=40),
        target=_ensure_str(payload.get("target"), default=fallback_target, max_length=80),
        rationale=_ensure_str(
            payload.get("rationale"),
            default="LLM did not return a rationale.",
            max_length=600,
        ),
        risk=_ensure_str(payload.get("risk"), default="medium", max_length=20).lower(),
        confidence=_ensure_float(payload.get("confidence"), default=0.7),
        runbook=_ensure_str(payload.get("runbook"), default="runbooks/general-triage.md", max_length=160),
        related_incidents=_ensure_list(payload.get("related_incidents"), max_items=3),
        dependency_services=_ensure_list(payload.get("dependency_services"), max_items=5),
        recent_changes=_ensure_list(payload.get("recent_changes"), max_items=3),
        workflow=_ensure_str(payload.get("workflow"), default="auto_remediate_with_approval", max_length=60),
        next_action=_ensure_str(payload.get("next_action"), default="Triage and mitigate"),
        requires_approval=_ensure_bool(payload.get("requires_approval"), default=True),
        downstream_agents=_ensure_list(
            payload.get("downstream_agents"),
            max_items=4,
        )
        or ["context-agent", "resolution-agent", "remediation-engine"],
        saturation=_ensure_str(payload.get("saturation"), default="elevated", max_length=20).lower(),
        trend=_ensure_str(payload.get("trend"), default="degrading", max_length=20).lower(),
        knowledge_base_entry=_ensure_str(
            payload.get("knowledge_base_entry"),
            default="Closure pending validation.",
            max_length=240,
        ),
        usage=usage,
    )
