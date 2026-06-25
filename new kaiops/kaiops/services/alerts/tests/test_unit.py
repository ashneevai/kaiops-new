from services.alerts.service import AlertService


class DummyRepository:
    def list(self, tenant_id: str):
        return [{"tenant_id": tenant_id}]


def test_service_list():
    svc = AlertService(DummyRepository())
    rows = svc.list("tenant-1")
    assert rows[0]["tenant_id"] == "tenant-1"
