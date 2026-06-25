from services.workflows.service import WorkflowService


class DummyRepository:
    def list(self, tenant_id: str):
        return [{"tenant_id": tenant_id}]


def test_service_list():
    svc = WorkflowService(DummyRepository())
    rows = svc.list("tenant-1")
    assert rows[0]["tenant_id"] == "tenant-1"
