from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db.session import get_db
from services.audit.repository import AuditLogRepository
from services.audit.schemas import AuditLogResponse
from services.audit.service import AuditLogService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse], summary="Audit management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = AuditLogService(AuditLogRepository(db))
    return service.list(tenant_id)
