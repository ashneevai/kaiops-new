from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Header, HTTPException

from services.sample_flows.data import CATALOG
from services.sample_flows.service import SampleFlowService

router = APIRouter(prefix="/sample", tags=["sample-flows"])

_ALERT_BODY = Body(default_factory=dict)


@router.get("/flows", summary="List demo incident flows")
def get_flows() -> dict[str, list[dict[str, str]]]:
    service = SampleFlowService()
    return {"flows": service.list_flows()}


@router.post("/from-alert/workflow", summary="Run agent workflow against a live alert payload")
async def post_workflow_from_alert(
    payload: dict[str, Any] = _ALERT_BODY,
    x_trace_id: str | None = Header(default=None, alias="x-trace-id"),
) -> dict[str, object]:
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(status_code=400, detail="Alert payload is required")
    service = SampleFlowService()
    return await service.run_workflow_from_alert(payload, trace_id=x_trace_id)


@router.post("/{flow_id}/workflow", summary="Run a demo end-to-end agent workflow")
async def post_flow_workflow(
    flow_id: str,
    x_trace_id: str | None = Header(default=None, alias="x-trace-id"),
) -> dict[str, object]:
    if flow_id not in CATALOG:
        raise HTTPException(status_code=404, detail=f"Unknown flow_id '{flow_id}'")
    service = SampleFlowService()
    return await service.run_workflow(flow_id=flow_id, trace_id=x_trace_id)
