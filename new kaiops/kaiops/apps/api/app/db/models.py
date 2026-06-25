from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.db.base import Base, BaseModelMixin


class Role(Base, BaseModelMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class RolePermission(Base, BaseModelMixin):
    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)
    permission_id: Mapped[str] = mapped_column(ForeignKey("permissions.id"), nullable=False, index=True)


class Permission(Base, BaseModelMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),)


class UserRole(Base, BaseModelMixin):
    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)


class Alert(Base, BaseModelMixin):
    __tablename__ = "alerts"

    external_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    service_name: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    dedupe_key: Mapped[str | None] = mapped_column(String(255), index=True)
    correlation_key: Mapped[str | None] = mapped_column(String(255), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    normalized_payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class Incident(Base, BaseModelMixin):
    __tablename__ = "incidents"

    alert_id: Mapped[str | None] = mapped_column(ForeignKey("alerts.id"))
    incident_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(40), nullable=False)
    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    impact_summary: Mapped[str | None] = mapped_column(Text)
    rca_summary: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))


class IncidentTimeline(Base, BaseModelMixin):
    __tablename__ = "incident_timelines"

    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class AgentExecution(Base, BaseModelMixin):
    __tablename__ = "agent_executions"

    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    execution_trace_id: Mapped[str | None] = mapped_column(String(255))


class Approval(Base, BaseModelMixin):
    __tablename__ = "approvals"

    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    requested_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    approver_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(Text)
    decision_notes: Mapped[str | None] = mapped_column(Text)


class Runbook(Base, BaseModelMixin):
    __tablename__ = "runbooks"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text, nullable=False)


class Automation(Base, BaseModelMixin):
    __tablename__ = "automations"

    incident_id: Mapped[str | None] = mapped_column(ForeignKey("incidents.id"))
    runbook_id: Mapped[str | None] = mapped_column(ForeignKey("runbooks.id"))
    provider: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=False)
    rollback_ref: Mapped[str | None] = mapped_column(String(255))
    result_payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class Workflow(Base, BaseModelMixin):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    definition: Mapped[dict] = mapped_column(JSONB, nullable=False)


class KnowledgeDocument(Base, BaseModelMixin):
    __tablename__ = "knowledge_documents"

    source: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    embedding_ref: Mapped[str | None] = mapped_column(String(255), index=True)


class KnowledgeEmbedding(Base, BaseModelMixin):
    __tablename__ = "knowledge_embeddings"

    document_id: Mapped[str] = mapped_column(ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)


class AuditLog(Base, BaseModelMixin):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)


class Notification(Base, BaseModelMixin):
    __tablename__ = "notifications"

    recipient_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    sent_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))


Index("ix_incidents_tenant_status", Incident.tenant_id, Incident.status)
Index("ix_alerts_tenant_source_status", Alert.tenant_id, Alert.source, Alert.status)
Index("ix_audit_tenant_action", AuditLog.tenant_id, AuditLog.action)
Index("ix_knowledge_embeddings_doc_chunk", KnowledgeEmbedding.document_id, KnowledgeEmbedding.chunk_index)
