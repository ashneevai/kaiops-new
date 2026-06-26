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
            agent_output = dict(result[agent_name])
            agent_output["llm_usage"] = self._estimate_llm_usage(
                agent_name=agent_name,
                input_payload=initial_state,
                output_payload=agent_output,
            )

            execution = models.AgentExecution(
                tenant_id=incident.tenant_id,
                incident_id=incident.id,
                agent_name=agent_name,
                status="completed",
                confidence_score=result[agent_name].get("confidence", result.get("confidence", 0)),
                input_payload=initial_state,
                output_payload=agent_output,
            )
            self.db.add(execution)

        incident.rca_summary = result["rca"].get("hypothesis")
        incident.impact_summary = result["impact"].get("blast_radius")
        self.db.commit()

        return result

    @staticmethod
    def _estimate_llm_usage(agent_name: str, input_payload: dict, output_payload: dict) -> dict:
        input_size = len(str(input_payload))
        output_size = len(str(output_payload))

        prompt_tokens = max(input_size // 4, 300)
        completion_tokens = max(output_size // 4, 120)
        total_tokens = prompt_tokens + completion_tokens

        model = "gpt-4o-mini"
        token_cost_per_1k_usd = 0.0008
        estimated_cost_usd = round((total_tokens / 1000) * token_cost_per_1k_usd, 6)

        return {
            "agent_name": agent_name,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "token_cost_per_1k_usd": token_cost_per_1k_usd,
            "estimated_cost_usd": estimated_cost_usd,
        }
