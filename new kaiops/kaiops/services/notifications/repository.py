from sqlalchemy.orm import Session

from app.db import models


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.Notification]:
        return (
            self.db.query(models.Notification)
            .filter(models.Notification.tenant_id == tenant_id, models.Notification.deleted_at.is_(None))
            .order_by(models.Notification.created_at.desc())
            .all()
        )
