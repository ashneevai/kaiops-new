from sqlalchemy.orm import Session

from app.db import models


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: str) -> list[models.User]:
        return (
            self.db.query(models.User)
            .filter(models.User.tenant_id == tenant_id, models.User.deleted_at.is_(None))
            .order_by(models.User.created_at.desc())
            .all()
        )
