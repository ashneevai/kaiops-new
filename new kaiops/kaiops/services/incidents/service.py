from services.incidents.repository import IncidentRepository


class IncidentService:
    def __init__(self, repository: IncidentRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
