from app.agents.state import AgentState


def context_agent(state: AgentState) -> AgentState:
    state["context"] = {
        "services": [state["alert"].get("service_name", "unknown")],
        "dependencies": ["postgres", "kafka", "redis"],
        "confidence": 78,
    }
    state["confidence"] = 78
    return state


def rca_agent(state: AgentState) -> AgentState:
    state["rca"] = {
        "hypothesis": "Database connection saturation",
        "evidence": ["high p95 latency", "db pool exhaustion"],
        "confidence": 74,
    }
    state["confidence"] = 74
    return state


def impact_agent(state: AgentState) -> AgentState:
    state["impact"] = {
        "blast_radius": "checkout-service",
        "users_affected": 12000,
        "estimated_revenue_risk_usd": 42000,
        "confidence": 80,
    }
    state["confidence"] = 80
    return state


def resolution_agent(state: AgentState) -> AgentState:
    state["resolution"] = {
        "plan": [
            "Scale read replicas",
            "Restart exhausted worker pods",
            "Apply circuit breaker thresholds",
        ],
        "automation_candidates": ["kubernetes", "terraform"],
        "confidence": 76,
    }
    state["confidence"] = 76
    return state


def validation_agent(state: AgentState) -> AgentState:
    state["validation"] = {
        "checks": ["error rate < 1%", "latency p95 < 300ms"],
        "result": "pending_approval",
        "confidence": 82,
    }
    state["approval"] = {
        "required": True,
        "reason": "Automation action with infra mutation",
    }
    state["confidence"] = 82
    return state
