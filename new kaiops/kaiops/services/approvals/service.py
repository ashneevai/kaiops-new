from services.approvals.repository import ApprovalRepository


class ApprovalService:
    def __init__(self, repository: ApprovalRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
