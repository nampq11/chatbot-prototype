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

import streamlit as st

from src.app.agent.workflow.state import BookingCareAgentState
from src.config import Config

config = Config()
set_verbose(True)

async def get_response(
    messages: str | list[str] | list[dict[str, Any]],
    bookingcare_id: str,
    bookingcare_name: str,
    bookingcare_perspective: str,
    bookingcare_style: str,
    bookingcare_context: str,
    new_thread: bool = False,
) -> AsyncGenerator[str, None]:
    graph_builder = create_workflow_graph()
    
    # Initialize MongoDB checkpoint saver
    checkpoint_saver = AsyncMongoDBSaver(
        conn_string=config.mongo.URI,
        db_name=config.mongo.DB_NAME,
        checkpoint_collection_name=config.mongo.STATE_CHECKPOINT_COLLECTION,
        writes_collection_name=config.mongo.STATE_WRITES_COLLECTION,
    )
    
    # Create a unique run ID for this conversation
    run_id = str(uuid.uuid4())
    
    # Initialize the graph with the checkpoint saver
    graph = graph_builder.build(
        checkpoint_saver=checkpoint_saver,
        run_id=run_id
    )
    
    # Create initial state
    state = BookingCareAgentState(
        messages=messages,
        bookingcare_id=bookingcare_id,
        bookingcare_name=bookingcare_name,
        bookingcare_perspective=bookingcare_perspective,
        bookingcare_style=bookingcare_style,
        bookingcare_context=bookingcare_context,
        new_thread=new_thread
    )
    
    # Run the graph
    async for event in graph.astream(state):
        if isinstance(event, AIMessageChunk):
            yield event.content
            
    # Get the final state
    final_state = await graph.aget_state()
    yield final_state

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
            conn_string=config.mongo.URI,
            db_name=config.mongo.DB_NAME,
            checkpoint_collection_name=config.mongo.STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=config.mongo.STATE_WRITES_COLLECTION,
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
            async for stream_mode, chunk in graph.astream(
                input={
                    "messages": __format_messages(messages),
                    "bookingcare_name": bookingcare_name,
                    "bookingcare_perspective": bookingcare_perspective,
                    "bookingcare_style": bookingcare_style,
                    "bookingcare_context": bookingcare_context,
                },
                config=graph_config,
                stream_mode=["messages", "updates"],
            ):
                logger.info(f"Stream mode: {stream_mode}")
                logger.info(f"Chunk: {chunk}")
                # chunk is a tuple of (message, metadata)
                if stream_mode == "messages":
                    message, metadata = chunk
                    if metadata["langgraph_node"] == "conversation_node" and isinstance(
                        message, AIMessageChunk
                    ):
                        yield stream_mode, message.content

                elif stream_mode == "updates":
                    yield stream_mode, chunk

        # final_state = await graph.aget_state()
        # yield final_state
                    
    except Exception as e:
        raise RuntimeError(f"Error running conversation workflow: {str(e)}") from e

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