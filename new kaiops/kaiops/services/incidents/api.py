from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db import models
from app.db.session import get_db
from services.incidents.repository import IncidentRepository
from services.incidents.schemas import IncidentResponse
from services.incidents.service import IncidentService

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentResponse], summary="Incident management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = IncidentService(IncidentRepository(db))
    return service.list(tenant_id)


@router.post("/{incident_id}/status/{status}", summary="Update incident status")
def update_status(
    incident_id: str,
    status: str,
    tenant_id: str = Depends(require_tenant),
    db: Session = Depends(get_db),
):
    allowed = {"open", "investigating", "mitigating", "resolved", "closed"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid incident status")

    incident = (
        db.query(models.Incident)
        .filter(models.Incident.id == incident_id, models.Incident.tenant_id == tenant_id)
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = status
    if status in {"resolved", "closed"} and not incident.resolved_at:
        incident.resolved_at = datetime.now(timezone.utc)

    db.add(
        models.IncidentTimeline(
            tenant_id=tenant_id,
            incident_id=incident.id,
            event_type="status_updated",
            message=f"Incident moved to {status}",
            event_payload={"status": status},
        )
    )
    db.commit()
    return {"incident_id": incident_id, "status": status}


@router.get("/{incident_id}/metrics", summary="Incident metrics")
def incident_metrics(incident_id: str, tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    incident = (
        db.query(models.Incident)
        .filter(models.Incident.id == incident_id, models.Incident.tenant_id == tenant_id)
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    mttr_minutes = None
    if incident.resolved_at:
        mttr_minutes = int((incident.resolved_at - incident.created_at).total_seconds() / 60)

    timeline_events = (
        db.query(models.IncidentTimeline)
        .filter(models.IncidentTimeline.incident_id == incident.id)
        .count()
    )

    return {
        "incident_id": incident_id,
        "status": incident.status,
        "timeline_events": timeline_events,
        "mttr_minutes": mttr_minutes,
    }
