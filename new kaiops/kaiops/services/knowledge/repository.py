from sqlalchemy.orm import Session

from app.db import models


class KnowledgeDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.KnowledgeDocument]:
        return (
            self.db.query(models.KnowledgeDocument)
            .filter(models.KnowledgeDocument.tenant_id == tenant_id, models.KnowledgeDocument.deleted_at.is_(None))
            .order_by(models.KnowledgeDocument.created_at.desc())
            .all()
        )
