from langgraph.graph import END, StateGraph

from app.agents.nodes import (
    context_agent,
    impact_agent,
    rca_agent,
    resolution_agent,
    validation_agent,
)
from app.agents.state import AgentState


def build_incident_graph():
    graph = StateGraph(AgentState)
    graph.add_node("context", context_agent)
    graph.add_node("rca", rca_agent)
    graph.add_node("impact", impact_agent)
    graph.add_node("resolution", resolution_agent)
    graph.add_node("validation", validation_agent)

    graph.set_entry_point("context")
    graph.add_edge("context", "rca")
    graph.add_edge("rca", "impact")
    graph.add_edge("impact", "resolution")
    graph.add_edge("resolution", "validation")
    graph.add_edge("validation", END)

    return graph.compile()


incident_graph = build_incident_graph()
