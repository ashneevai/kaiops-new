from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.platform.auth import decode_jwt


class RBACMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        permission_rules: dict[tuple[str, str], str],
        exempt_paths: set[str],
        exempt_path_prefixes: tuple[str, ...] = (),
    ):
        super().__init__(app)
        self.permission_rules = permission_rules
        self.exempt_paths = exempt_paths
        self.exempt_path_prefixes = exempt_path_prefixes

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        method = request.method.upper()

        if (
            path in self.exempt_paths
            or path.startswith("/docs")
            or path.startswith("/openapi")
            or any(path.startswith(prefix) for prefix in self.exempt_path_prefixes)
        ):
            return await call_next(request)

        if not path.startswith("/api/v1"):
            return await call_next(request)

        required_permission = self._resolve_permission(path, method)
        if not required_permission:
            return JSONResponse(status_code=403, content={"detail": "Route is missing RBAC mapping"})

        auth_header = request.headers.get("authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing bearer token"})

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_jwt(token)
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid bearer token"})
        roles = set(payload.get("roles", []))
        permissions = set(payload.get("permissions", []))

        if required_permission not in permissions and "admin" not in roles:
            return JSONResponse(status_code=403, content={"detail": "Insufficient permissions"})

        request.state.user = payload
        return await call_next(request)

    def _resolve_permission(self, path: str, method: str) -> str | None:
        candidates = []
        for (prefix, verb), permission in self.permission_rules.items():
            if path.startswith(prefix) and verb == method:
                candidates.append((len(prefix), permission))

        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]


PERMISSION_RULES: dict[tuple[str, str], str] = {
    ("/api/v1/alerts", "GET"): "alerts:read",
    ("/api/v1/alerts", "POST"): "alerts:write",
    ("/api/v1/alerts/ingest", "POST"): "alerts:write",
    ("/api/v1/incidents", "GET"): "incidents:read",
    ("/api/v1/incidents", "POST"): "incidents:write",
    ("/api/v1/incidents/", "POST"): "incidents:write",
    ("/api/v1/incidents/", "GET"): "incidents:read",
    ("/api/v1/workflows", "GET"): "workflows:read",
    ("/api/v1/workflows", "POST"): "workflows:write",
    ("/api/v1/approvals", "GET"): "approvals:read",
    ("/api/v1/approvals", "POST"): "approvals:write",
    ("/api/v1/automations", "GET"): "automations:read",
    ("/api/v1/automations", "POST"): "automations:execute",
    ("/api/v1/knowledge", "GET"): "knowledge:read",
    ("/api/v1/knowledge", "POST"): "knowledge:write",
    ("/api/v1/knowledge/index", "POST"): "knowledge:write",
    ("/api/v1/knowledge/retrieve", "GET"): "knowledge:read",
    ("/api/v1/audit", "GET"): "audit:read",
    ("/api/v1/users", "GET"): "users:read",
    ("/api/v1/users", "POST"): "users:write",
    ("/api/v1/notifications", "GET"): "notifications:read",
    ("/api/v1/notifications", "POST"): "notifications:write",
    ("/api/v1/agents", "POST"): "agents:execute",
    ("/api/v1/agents/incidents/", "POST"): "agents:execute",
}

EXEMPT_PATHS = {
    "/health",
    "/api/v1/auth/token",
    "/api/v1/monitoring/overview",
    "/api/v1/monitoring/alerts",
    "/api/v1/monitoring/llmops",
    "/api/v1/sample/flows",
}

EXEMPT_PATH_PREFIXES: tuple[str, ...] = ("/api/v1/sample/",)
