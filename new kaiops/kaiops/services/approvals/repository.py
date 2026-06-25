from sqlalchemy.orm import Session

from app.db import models


class ApprovalRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.Approval]:
        return (
            self.db.query(models.Approval)
            .filter(models.Approval.tenant_id == tenant_id, models.Approval.deleted_at.is_(None))
            .order_by(models.Approval.created_at.desc())
            .all()
        )
