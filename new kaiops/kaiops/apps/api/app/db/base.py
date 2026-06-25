from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class BaseModelMixin:
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=True), index=True)
