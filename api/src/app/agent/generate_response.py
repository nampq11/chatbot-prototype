import os
import uuid
from langchain.globals import set_verbose
from loguru import logger
from typing import Any, AsyncGenerator, Union
from langchain_core.messages import AIMessage, AIMessage, HumanMessage, AIMessageChunk
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from opik.integrations.langchain import OpikTracer

from src.app.agent.workflow.graph import (
    create_workflow_graph,
)

from src.app.agent.workflow.state import BookingCareAgentState
from src.config import settings

set_verbose(True)

async def get_response(
    messages: str | list[str] | list[dict[str, Any]],
    bookingcare_id: str,
    bookingcare_name: str,
    bookingcare_perspective: str,
    bookingcare_style: str,
    bookingcare_context: str,
    new_thread: bool = False,
) -> tuple[str, BookingCareAgentState]:
    graph_builder = create_workflow_graph()
    
    try:
        async with AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.DB_NAME,
            checkpoint_collection_name=settings.STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=settings.STATE_WRITES_COLLECTION,
        ) as checkpointer:
            graph = graph_builder.compile(checkpointer=checkpointer)
            opik_tracer = OpikTracer(graph=graph.get_graph(xray=True))

            thread_id = (
                bookingcare_id if not new_thread else f"{bookingcare_id}-{uuid.uuid4()}"
            )

            config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [opik_tracer],
            }

            output_state = await graph.ainvoke(
                input={
                    "messages": __format_messages(messages),
                    "bookingcare_name": bookingcare_name,
                    "bookingcare_perspective": bookingcare_perspective,
                    "bookingcare_style": bookingcare_style,
                    "bookingcare_context": bookingcare_context,
                },
                config=config,
            )
            last_message = output_state["messages"][-1]
            return last_message.content, BookingCareAgentState(**output_state)
    except Exception as e:
        raise RuntimeError(f"Error running conversation workflow: {str(e)}") from e
    
async def get_streaming_response(
    messages: str | list[str] | list[dict[str, Any]],
    bookingcare_id: str,
    bookingcare_name: str,
    bookingcare_perspective: str,
    bookingcare_style: str,
    bookingcare_context: str,
    new_thread: bool = False,
) -> AsyncGenerator[str, None]:
    graph_builder = create_workflow_graph()

    try:
        async with AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.DB_NAME,
            checkpoint_collection_name=settings.LONG_TERM_MEMORY_COLLECTION,
            writes_collection_name=settings.STATE_WRITES_COLLECTION,
        ) as checkpointer:
            graph = graph_builder.compile(checkpointer=checkpointer)
            opik_tracer = OpikTracer(graph=graph.get_graph(xray=True))

            thread_id = (
                bookingcare_id if not new_thread else f"{bookingcare_id}-{uuid.uuid4()}"
            )
            graph_config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [opik_tracer],
            }
            async for chunk in graph.astream(
                input={
                    "messages": __format_messages(messages),
                    "bookingcare_name": bookingcare_name,
                    "bookingcare_perspective": bookingcare_perspective,
                    "bookingcare_style": bookingcare_style,
                    "bookingcare_context": bookingcare_context,
                },
                config=graph_config,
                stream_mode=["messages"],
            ):
                if chunk[1]['langgraph_node'] == 'conversation_node' and isinstance(
                   chunk[0], AIMessageChunk
                ):
                    yield chunk[0].content
                    
    except Exception as e:
        raise RuntimeError(
            f"Error running conversation workflow: {str(e)}"
        ) from e

def __format_messages(
    messages: Union[str, list[dict[str, Any]]]
) -> list[Union[HumanMessage, AIMessage]]:
    
    if isinstance(messages, dict):
        if messages["role"] == "user":
            return [HumanMessage(content=messages["content"])]
        elif messages["role"] == "assistant":
            return [AIMessage(content=messages["content"])]
    
    if isinstance(messages, str):
        return [HumanMessage(content=messages)]
    
    if isinstance(messages, list):
        if not messages:
            return []

        if (
            isinstance(messages[0], dict)
            and "role" in messages[0]
            and "content" in messages[0]
        ):
            result = []
            for msg in messages:
                if msg["role"] == "user":
                    result.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    result.append(AIMessage(content=msg["content"]))
            return result
        
        return [HumanMessage(content=message) for message in messages]
    
    return []