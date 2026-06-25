from fastapi import APIRouter

from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def issue_token(username: str, tenant_id: str, role: str = "operator"):
    role_permissions = {
        "admin": [
            "alerts:read",
            "alerts:write",
            "incidents:read",
            "incidents:write",
            "workflows:read",
            "workflows:write",
            "approvals:read",
            "approvals:write",
            "automations:read",
            "automations:execute",
            "knowledge:read",
            "knowledge:write",
            "audit:read",
            "users:read",
            "users:write",
            "notifications:read",
            "notifications:write",
            "agents:execute",
        ],
        "operator": [
            "alerts:read",
            "alerts:write",
            "incidents:read",
            "incidents:write",
            "workflows:read",
            "approvals:read",
            "automations:read",
            "automations:execute",
            "knowledge:read",
            "notifications:read",
            "agents:execute",
        ],
        "viewer": [
            "alerts:read",
            "incidents:read",
            "workflows:read",
            "approvals:read",
            "automations:read",
            "knowledge:read",
            "audit:read",
            "notifications:read",
        ],
    }
    permissions = role_permissions.get(role, role_permissions["viewer"])
    token = create_access_token(
        subject=username,
        tenant_id=tenant_id,
        roles=[role],
        permissions=permissions,
    )
    return {"access_token": token, "token_type": "bearer", "role": role, "permissions": permissions}
