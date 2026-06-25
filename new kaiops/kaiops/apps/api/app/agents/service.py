from sqlalchemy.orm import Session

from app.agents.orchestrator import incident_graph
from app.db import models


class AgentRuntimeService:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, incident: models.Incident, alert: models.Alert) -> dict:
        initial_state = {
            "tenant_id": str(incident.tenant_id),
            "incident_id": str(incident.id),
            "alert": {
                "id": str(alert.id),
                "service_name": alert.service_name,
                "severity": alert.severity,
                "source": alert.source,
            },
            "context": {},
            "rca": {},
            "impact": {},
            "resolution": {},
            "validation": {},
            "approval": {},
            "confidence": 0,
        }
        result = incident_graph.invoke(initial_state)

        for agent_name in ["context", "rca", "impact", "resolution", "validation"]:
            execution = models.AgentExecution(
                tenant_id=incident.tenant_id,
                incident_id=incident.id,
                agent_name=agent_name,
                status="completed",
                confidence_score=result[agent_name].get("confidence", result.get("confidence", 0)),
                input_payload=initial_state,
                output_payload=result[agent_name],
            )
            self.db.add(execution)

        incident.rca_summary = result["rca"].get("hypothesis")
        incident.impact_summary = result["impact"].get("blast_radius")
        self.db.commit()

        return result
