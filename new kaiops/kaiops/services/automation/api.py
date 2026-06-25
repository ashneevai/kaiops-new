from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db.session import get_db
from services.automation.repository import AutomationRepository
from services.automation.schemas import (
    AutomationExecuteRequest,
    AutomationExecuteResponse,
    AutomationResponse,
)
from services.automation.service import AutomationService

router = APIRouter(prefix="/automations", tags=["automation"])


@router.get("", response_model=list[AutomationResponse], summary="Automation management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = AutomationService(AutomationRepository(db))
    return service.list(tenant_id)


@router.post("/execute", response_model=AutomationExecuteResponse, summary="Execute automation adapter")
def execute_automation(
    request: AutomationExecuteRequest,
    tenant_id: str = Depends(require_tenant),
    db: Session = Depends(get_db),
):
    service = AutomationService(AutomationRepository(db))
    try:
        result = service.execute(
            tenant_id=tenant_id,
            provider=request.provider,
            action=request.action,
            payload=request.payload,
            dry_run=request.dry_run,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AutomationExecuteResponse(**result)
