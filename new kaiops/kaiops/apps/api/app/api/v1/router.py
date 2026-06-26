from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.auth import router as auth_router
from app.api.v1.monitoring import router as monitoring_router
from services.alerts.api import router as alerts_router
from services.approvals.api import router as approvals_router
from services.audit.api import router as audit_router
from services.automation.api import router as automation_router
from services.incidents.api import router as incidents_router
from services.knowledge.api import router as knowledge_router
from services.notifications.api import router as notifications_router
from services.users.api import router as users_router
from services.workflows.api import router as workflows_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(monitoring_router)
api_router.include_router(alerts_router)
api_router.include_router(incidents_router)
api_router.include_router(workflows_router)
api_router.include_router(approvals_router)
api_router.include_router(automation_router)
api_router.include_router(knowledge_router)
api_router.include_router(audit_router)
api_router.include_router(users_router)
api_router.include_router(notifications_router)
api_router.include_router(agents_router)
