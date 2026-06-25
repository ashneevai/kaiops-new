from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db.session import get_db
from services.workflows.repository import WorkflowRepository
from services.workflows.schemas import WorkflowResponse
from services.workflows.service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowResponse], summary="Workflow management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = WorkflowService(WorkflowRepository(db))
    return service.list(tenant_id)
