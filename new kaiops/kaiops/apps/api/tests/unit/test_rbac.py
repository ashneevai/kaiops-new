from app.platform.rbac import RBACMiddleware


class DummyApp:
    pass


def test_rbac_permission_resolution_longest_prefix():
    middleware = RBACMiddleware(
        app=DummyApp(),
        permission_rules={
            ("/api/v1/alerts", "GET"): "alerts:read",
            ("/api/v1/alerts/ingest", "GET"): "alerts:ingest:read",
        },
        exempt_paths=set(),
    )

    permission = middleware._resolve_permission("/api/v1/alerts/ingest", "GET")
    assert permission == "alerts:ingest:read"
