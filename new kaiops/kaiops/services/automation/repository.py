from sqlalchemy.orm import Session

from app.db import models


class AutomationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.Automation]:
        return (
            self.db.query(models.Automation)
            .filter(models.Automation.tenant_id == tenant_id, models.Automation.deleted_at.is_(None))
            .order_by(models.Automation.created_at.desc())
            .all()
        )

    def create_execution(
        self,
        tenant_id: str,
        provider: str,
        dry_run: bool,
        result_payload: dict,
        incident_id: str | None = None,
        runbook_id: str | None = None,
    ) -> models.Automation:
        row = models.Automation(
            tenant_id=tenant_id,
            provider=provider,
            dry_run=dry_run,
            status=result_payload.get("status", "submitted"),
            result_payload=result_payload,
            incident_id=incident_id,
            runbook_id=runbook_id,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
