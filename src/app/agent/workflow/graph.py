from functools import lru_cache

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition

from src.app.agent.workflow.edges import should_summarize_conversation

from src.app.agent.workflow.nodes import (
    conversation_node,
    summarize_conversation_node,
    summarize_context_node,
    retriever_node,
    connector_node,
)

from src.app.agent.workflow.state import BookingCareAgentState

@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(BookingCareAgentState)

    # Add all nodes
    graph_builder.add_node("conversation_node", conversation_node)
    graph_builder.add_node("retriever_context", retriever_node)
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)
    graph_builder.add_node("summarize_context_node", summarize_context_node)
    graph_builder.add_node("connector_node", connector_node)

    # Define the flow
    graph_builder.add_edge(START, "conversation_node")
    graph_builder.add_conditional_edges(
        "conversation_node",
        tools_condition,
        {
            "tools": "retriever_context",
            END: "connector_node",
        }
    )
    graph_builder.add_edge("retriever_context", "summarize_context_node")
    graph_builder.add_edge("summarize_context_node", "conversation_node")
    graph_builder.add_conditional_edges(
        "connector_node",
        should_summarize_conversation
    )
    graph_builder.add_edge("summarize_conversation_node", END)

    return graph_builder

graph = create_workflow_graph().compile()