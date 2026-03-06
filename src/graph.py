from langgraph.graph import StateGraph, START, END

from src.state import MwemaAgentState
from src.agents.concierge import supervisor_node, general_chat_node
from src.agents.catalog import catalog_agent_node
from src.agents.booking import booking_agent_node
from src.agents.faq import faq_agent_node


def route_by_intent(state: MwemaAgentState) -> str:
    intent = state.get("current_intent", "general")
    return {
        "buy": "catalog_agent",
        "book": "booking_agent",
        "info": "faq_agent",
        "general": "general_chat",
    }.get(intent, "general_chat")


def create_mwema_graph():
    builder = StateGraph(MwemaAgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("catalog_agent", catalog_agent_node)
    builder.add_node("booking_agent", booking_agent_node)
    builder.add_node("faq_agent", faq_agent_node)
    builder.add_node("general_chat", general_chat_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_by_intent)
    builder.add_edge("catalog_agent", END)
    builder.add_edge("booking_agent", END)
    builder.add_edge("faq_agent", END)
    builder.add_edge("general_chat", END)

    return builder.compile()
