from typing_extensions import Literal

from langgraph.graph import END

from src.app.agent.workflow.state import BookingCareAgentState
from src.config import Config

config = Config()

def should_summarize_conversation(
    state: BookingCareAgentState
) -> Literal["summarize_conversation_node", "__end__"]:
    messages = state["messages"]

    if len(messages) > config.TOTAL_MESSAGES_SUMMARY_TRIGGER:
        return "summarize_conversation_node"
    
    return END