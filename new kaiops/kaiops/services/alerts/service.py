from services.alerts.repository import AlertRepository


class AlertService:
    def __init__(self, repository: AlertRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
