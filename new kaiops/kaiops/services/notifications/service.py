from services.notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
