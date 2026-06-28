"""
Task 1 & 4: LangGraph workflow design and conditional routing.
Builds the full customer support automation graph.
"""

from langgraph.graph import StateGraph, END
from state import SupportState
from agents import (
    classify_intent,
    sales_agent,
    technical_agent,
    billing_agent,
    account_agent,
    memory_agent,
    human_approval_node,
    supervisor_agent,
)


# ─────────────────────────────────────────────
# ROUTING FUNCTIONS (Task 4)
# ─────────────────────────────────────────────

def route_by_intent(state: SupportState) -> str:
    """Route query to appropriate department after intent classification."""
    intent = state.get("intent", "sales")
    routing_map = {
        "sales": "sales_agent",
        "technical": "technical_agent",
        "billing": "billing_agent",
        "account": "account_agent",
        "memory": "memory_agent",
    }
    destination = routing_map.get(intent, "sales_agent")
    print(f"[Router] Routing to: {destination}")
    return destination


def route_after_agent(state: SupportState) -> str:
    """After agent responds, check if human approval is needed."""
    if state.get("requires_human_approval", False):
        print("[Router] Escalating to human approval.")
        return "human_approval"
    return "supervisor"


# ─────────────────────────────────────────────
# BUILD GRAPH (Task 1)
# ─────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(SupportState)

    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("sales_agent", sales_agent)
    graph.add_node("technical_agent", technical_agent)
    graph.add_node("billing_agent", billing_agent)
    graph.add_node("account_agent", account_agent)
    graph.add_node("memory_agent", memory_agent)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("supervisor", supervisor_agent)

    # Entry point
    graph.set_entry_point("classify_intent")

    # Intent → department routing (Task 4)
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "sales_agent": "sales_agent",
            "technical_agent": "technical_agent",
            "billing_agent": "billing_agent",
            "account_agent": "account_agent",
            "memory_agent": "memory_agent",
        },
    )

    # After each agent → check if human approval needed
    for agent_node in ["sales_agent", "technical_agent", "billing_agent", "account_agent", "memory_agent"]:
        graph.add_conditional_edges(
            agent_node,
            route_after_agent,
            {
                "human_approval": "human_approval",
                "supervisor": "supervisor",
            },
        )

    # Human approval → supervisor
    graph.add_edge("human_approval", "supervisor")

    # Supervisor → END
    graph.add_edge("supervisor", END)

    return graph.compile()


# Singleton compiled graph
support_graph = build_graph()
