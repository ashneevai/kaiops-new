from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db.session import get_db
from services.approvals.repository import ApprovalRepository
from services.approvals.schemas import ApprovalResponse
from services.approvals.service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalResponse], summary="Approval management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = ApprovalService(ApprovalRepository(db))
    return service.list(tenant_id)
