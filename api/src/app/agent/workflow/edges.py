from typing_extensions import Literal

from langgraph.graph import END

from src.app.agent.workflow.state import BookingCareAgentState
from src.config import settings

def should_summarize_conversation(
    state: BookingCareAgentState
) -> Literal["summarize_conversation_node", "__end__"]:
    messages = state["messages"]

    if len(messages) > settings.TOTAL_MESSAGES_SUMMARY_TRIGGER:
        return "summarize_conversation_node"
    
    return END