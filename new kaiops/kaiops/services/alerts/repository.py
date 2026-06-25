from sqlalchemy.orm import Session

from app.db import models


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.Alert]:
        return (
            self.db.query(models.Alert)
            .filter(models.Alert.tenant_id == tenant_id, models.Alert.deleted_at.is_(None))
            .order_by(models.Alert.created_at.desc())
            .all()
        )
