from sqlalchemy.orm import Session

from app.db import models


class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.Incident]:
        return (
            self.db.query(models.Incident)
            .filter(models.Incident.tenant_id == tenant_id, models.Incident.deleted_at.is_(None))
            .order_by(models.Incident.created_at.desc())
            .all()
        )
