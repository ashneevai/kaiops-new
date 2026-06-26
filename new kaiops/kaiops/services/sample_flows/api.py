from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from services.sample_flows.data import SCENARIOS
from services.sample_flows.service import SampleFlowService

router = APIRouter(prefix="/sample", tags=["sample-flows"])


@router.get("/flows", summary="List demo incident flows")
def get_flows() -> dict[str, list[dict[str, str]]]:
    service = SampleFlowService()
    return {"flows": service.list_flows()}


@router.post("/{flow_id}/workflow", summary="Run a demo end-to-end agent workflow")
def post_flow_workflow(
    flow_id: str,
    x_trace_id: str | None = Header(default=None, alias="x-trace-id"),
) -> dict[str, object]:
    if flow_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Unknown flow_id '{flow_id}'")
    service = SampleFlowService()
    return service.run_workflow(flow_id=flow_id, trace_id=x_trace_id)
