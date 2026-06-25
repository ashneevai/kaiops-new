from pydantic import BaseModel, Field


class AlertIngestionRequest(BaseModel):
    source: str = Field(description="Alert source system")
    payload: dict = Field(description="Raw source payload")


class AlertIngestionResponse(BaseModel):
    alert_id: str
    deduplicated: bool
    incident_id: str | None
