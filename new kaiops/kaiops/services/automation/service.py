from services.automation.repository import AutomationRepository
from services.automation.providers import get_provider


class AutomationService:
    def __init__(self, repository: AutomationRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)

    def execute(
        self,
        tenant_id: str,
        provider: str,
        action: str,
        payload: dict,
        dry_run: bool = False,
    ) -> dict:
        adapter = get_provider(provider)
        result = adapter.execute(action=action, payload=payload, dry_run=dry_run)
        self.repository.create_execution(
            tenant_id=tenant_id,
            provider=provider,
            dry_run=dry_run,
            result_payload=result,
            incident_id=payload.get("incident_id"),
            runbook_id=payload.get("runbook_id"),
        )
        return {
            "provider": provider,
            "action": action,
            "dry_run": dry_run,
            "status": result.get("status", "submitted"),
            "result": result,
        }
