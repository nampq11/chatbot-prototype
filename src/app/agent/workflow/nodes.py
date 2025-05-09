from langchain_core.messages import RemoveMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode

from src.app.agent.workflow.chains import (
    get_bookingcare_response_chain,
    get_conversation_summary_chain,
    get_context_summary_chain,
)

from src.app.agent.workflow.state import BookingCareAgentState
from src.app.agent.workflow.tools import tools
from src.config import Config

config = Config()

retriever_node = ToolNode(tools)

async def conversation_node(
    state: BookingCareAgentState,
    config: RunnableConfig
):
    summary = state.get("summary", "")
    conversation_chain = get_bookingcare_response_chain()

    response = await conversation_chain.ainvoke(
        {
            "messages": state["messages"],
            "bookingcare_context": state["bookingcare_context"],
            "bookingcare_name": state["bookingcare_name"],
            "bookingcare_perspective": state["bookingcare_perspective"],
            "bookingcare_style": state["bookingcare_style"],
            "summary": summary,
        },
        config,
    )

    return {"messages": response}

async def summarize_conversation_node(
  state: BookingCareAgentState,
):
    summary = state.get("summary", "")
    summary_chain = get_conversation_summary_chain(summary=summary)

    response = await summary_chain.ainvoke(
        {
            "messages": state["messages"],
            "bookingcare_name": state["bookingcare_name"],
            "summary": summary,
        }
    )

    delete_messages = [
        RemoveMessage(id=m.id)
        for m in state["messages"][: -config.message.TOTAL_MESSAGES_AFTER_SUMMARY]
    ]
    return {"summary": response.content, "messages": delete_messages}

async def summarize_context_node(
    state: BookingCareAgentState
):
    context_summary_chain = get_context_summary_chain()

    response = await context_summary_chain.ainvoke(
        {
            "context": state["messages"][-1].content,
        }
    )
    state["messages"][-1].content = response.content

    return {}

async def connector_node(
    state: BookingCareAgentState
):
    return {}