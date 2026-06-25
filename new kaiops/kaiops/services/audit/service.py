from services.audit.repository import AuditLogRepository


class AuditLogService:
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
