from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.agents.service import AgentRuntimeService
from app.db import models
from app.db.session import get_db

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/incidents/{incident_id}/execute")
def execute_agents(incident_id: str, tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    incident = (
        db.query(models.Incident)
        .filter(models.Incident.id == incident_id, models.Incident.tenant_id == tenant_id)
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    alert = db.query(models.Alert).filter(models.Alert.id == incident.alert_id).first()
    if not alert:
        raise HTTPException(status_code=400, detail="Incident has no related alert")

    service = AgentRuntimeService(db)
    result = service.execute(incident, alert)
    return {"incident_id": incident_id, "result": result}
