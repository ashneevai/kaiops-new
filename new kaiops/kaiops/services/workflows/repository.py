from sqlalchemy.orm import Session

from app.db import models


class WorkflowRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.Workflow]:
        return (
            self.db.query(models.Workflow)
            .filter(models.Workflow.tenant_id == tenant_id, models.Workflow.deleted_at.is_(None))
            .order_by(models.Workflow.created_at.desc())
            .all()
        )
