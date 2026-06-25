from services.users.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
