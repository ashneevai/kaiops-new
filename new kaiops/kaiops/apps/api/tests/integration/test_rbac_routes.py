from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.v1.dependencies import require_tenant
from app.core.security import create_access_token
from app.main import app


class FakeQuery:
    def __init__(self, model, db):
        self.model = model
        self.db = db

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def count(self):
        return 0

    def delete(self):
        return 0


class FakeSession:
    def query(self, model):
        return FakeQuery(model, self)

    def add(self, row):
        if not getattr(row, "id", None):
            row.id = uuid4()

    def flush(self):
        return None

    def commit(self):
        return None

    def close(self):
        return None


async def fake_publish(*args, **kwargs):
    return None


def fake_db_override():
    session = FakeSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def override_dependencies():
    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[require_tenant] = lambda: "tenant-1"
    from app.db.session import get_db

    app.dependency_overrides[get_db] = fake_db_override
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


def test_alerts_route_requires_rbac_token(monkeypatch):
    monkeypatch.setattr("app.platform.messaging.kafka_publisher.publish", fake_publish)
    with TestClient(app) as client:
        response = client.get("/api/v1/alerts", headers={"x-tenant-id": "tenant-1"})
        assert response.status_code == 401


def test_alerts_route_allows_authorized_user(monkeypatch):
    monkeypatch.setattr("app.platform.messaging.kafka_publisher.publish", fake_publish)
    token = create_access_token(
        subject="operator-1",
        tenant_id="tenant-1",
        roles=["operator"],
        permissions=["alerts:read", "alerts:write"],
    )
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/alerts",
            headers={"x-tenant-id": "tenant-1", "authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == []


def test_alert_ingest_route_allows_authorized_user(monkeypatch):
    monkeypatch.setattr("app.platform.messaging.kafka_publisher.publish", fake_publish)
    token = create_access_token(
        subject="operator-1",
        tenant_id="tenant-1",
        roles=["operator"],
        permissions=["alerts:write"],
    )
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/alerts/ingest",
            headers={"x-tenant-id": "tenant-1", "authorization": f"Bearer {token}"},
            json={"source": "prometheus", "payload": {"title": "API latency spike", "severity": "critical", "service": "checkout"}},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["deduplicated"] is False
        assert body["alert_id"]
        assert body["incident_id"]


def test_knowledge_retrieve_route_allows_authorized_user(monkeypatch):
    monkeypatch.setattr("app.platform.messaging.kafka_publisher.publish", fake_publish)
    token = create_access_token(
        subject="viewer-1",
        tenant_id="tenant-1",
        roles=["viewer"],
        permissions=["knowledge:read"],
    )
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/knowledge/retrieve",
            params={"q": "database saturation"},
            headers={"x-tenant-id": "tenant-1", "authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"results": []}
