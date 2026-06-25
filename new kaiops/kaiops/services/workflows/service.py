from services.workflows.repository import WorkflowRepository


class WorkflowService:
    def __init__(self, repository: WorkflowRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
