from sqlalchemy.orm import Session

from app.db import models


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.AuditLog]:
        return (
            self.db.query(models.AuditLog)
            .filter(models.AuditLog.tenant_id == tenant_id, models.AuditLog.deleted_at.is_(None))
            .order_by(models.AuditLog.created_at.desc())
            .all()
        )
