from services.users.service import UserService


class DummyRepository:
    def list(self, tenant_id: str):
        return [{"tenant_id": tenant_id}]


def test_service_list():
    svc = UserService(DummyRepository())
    rows = svc.list("tenant-1")
    assert rows[0]["tenant_id"] == "tenant-1"
