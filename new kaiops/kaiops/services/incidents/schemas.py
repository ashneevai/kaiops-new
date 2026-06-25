from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class IncidentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
