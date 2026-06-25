from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db.session import get_db
from services.notifications.repository import NotificationRepository
from services.notifications.schemas import NotificationResponse
from services.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse], summary="Notification management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = NotificationService(NotificationRepository(db))
    return service.list(tenant_id)
