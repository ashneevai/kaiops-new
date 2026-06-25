from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db import models
from app.db.session import get_db
from app.platform.messaging import kafka_publisher
from services.alerts.contracts import AlertIngestionRequest, AlertIngestionResponse
from services.alerts.ingestion import AlertIngestionService
from services.alerts.repository import AlertRepository
from services.alerts.schemas import AlertResponse
from services.alerts.service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse], summary="Alert management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = AlertService(AlertRepository(db))
    return service.list(tenant_id)


@router.post("/ingest", response_model=AlertIngestionResponse, summary="Ingest and correlate alerts")
async def ingest_alert(
    request: AlertIngestionRequest,
    tenant_id: str = Depends(require_tenant),
    db: Session = Depends(get_db),
):
    ingestion = AlertIngestionService()
    normalized = ingestion.normalize(request.source, request.payload)

    existing = (
        db.query(models.Alert)
        .filter(models.Alert.tenant_id == tenant_id, models.Alert.dedupe_key == normalized["dedupe_key"])
        .first()
    )
    deduplicated = existing is not None

    if existing:
        alert = existing
    else:
        alert = models.Alert(
            tenant_id=tenant_id,
            external_id=normalized["external_id"],
            source=normalized["source"],
            status=normalized["status"],
            severity=normalized["severity"],
            service_name=normalized["service_name"],
            title=normalized["title"],
            description=normalized["description"],
            dedupe_key=normalized["dedupe_key"],
            correlation_key=normalized["correlation_key"],
            payload=request.payload,
            normalized_payload=normalized,
        )
        db.add(alert)
        db.flush()

    incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.tenant_id == tenant_id,
            models.Incident.status.in_(["open", "investigating", "mitigating"]),
            models.Incident.alert_id == alert.id,
        )
        .first()
    )

    incident_id = None
    if not incident:
        incident = models.Incident(
            tenant_id=tenant_id,
            alert_id=alert.id,
            incident_key=f"INC-{uuid4().hex[:8].upper()}",
            title=alert.title,
            status="open",
            priority=alert.severity,
        )
        db.add(incident)
        db.flush()

        db.add(
            models.IncidentTimeline(
                tenant_id=tenant_id,
                incident_id=incident.id,
                event_type="incident_created",
                message="Incident created from alert ingestion",
                event_payload={"alert_id": str(alert.id), "source": alert.source},
            )
        )

    incident_id = str(incident.id)
    db.commit()

    await kafka_publisher.publish(
        "alerts",
        {
            "tenant_id": tenant_id,
            "alert_id": str(alert.id),
            "incident_id": incident_id,
            "severity": alert.severity,
            "source": alert.source,
            "deduplicated": deduplicated,
        },
    )

    return AlertIngestionResponse(alert_id=str(alert.id), deduplicated=deduplicated, incident_id=incident_id)
