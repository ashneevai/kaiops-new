from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db.session import get_db
from services.users.repository import UserRepository
from services.users.schemas import UserResponse
from services.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse], summary="User management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = UserService(UserRepository(db))
    return service.list(tenant_id)
