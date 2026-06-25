from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class AutomationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AutomationExecuteRequest(BaseModel):
    provider: str
    action: str
    payload: dict
    dry_run: bool = False


class AutomationExecuteResponse(BaseModel):
    provider: str
    action: str
    dry_run: bool
    status: str
    result: dict
