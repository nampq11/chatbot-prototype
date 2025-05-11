from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from opik.integrations.langchain import OpikTracer
from pydantic import BaseModel

from src.app.agent.generate_response import (
    get_response,
    get_streaming_response,
)
from src.app.agent.reset_conversation import (
    reset_conversation_state,
)
from src.domain.domain import DomainFactory
from .opik_utils import configure

configure()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """handle startup and shutdown events for the API."""
    # Startup code (if any) goes here
    yield
    # Shutdown code goes here
    opik_tracer = OpikTracer()
    opik_tracer.flush()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    domain_id: str

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        domain_factory = DomainFactory()
        domain = domain_factory.get_domain(chat_message.domain_id)
        response, _ = get_response(
            messages=chat_message.message,
            bookingcare_id=domain.id,
            bookingcare_name=domain.name,
            bookingcare_perspective=domain.perspective,
            bookingcare_style=domain.style,
            bookingcare_context=""
        )
        return {"response": response}
    except Exception as e:
        opik_tracer = OpikTracer()
        opik_tracer.flush()

        raise HTTPException(status_code=500, detail=str(e))
    
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            if "message" not in data or "domain_id" not in data:
                await websocket.send_json(
                    {
                        "error": "Invalid message format. Required fields: 'message' and 'domain_id'"
                    },
                )
                continue
            try:
                domain_factory = DomainFactory()
                domain = domain_factory.get_domain(data["domain_id"])

                response_stream = get_streaming_response(
                    messages=data["message"],
                    bookingcare_id=domain.id,
                    bookingcare_name=domain.name,
                    bookingcare_perspective=domain.perspective,
                    bookingcare_style=domain.style,
                    bookingcare_context=""
                )

                await websocket.send_json({"streaming": True})

                full_response = ""
                async for chunk in response_stream:
                    full_response += chunk
                    await websocket.send_json({"chunk": chunk})

                await websocket.send_json(
                    {"response": full_response, "streaming": False}
                )        
            except Exception as e:
                opik_tracer = OpikTracer()
                opik_tracer.flush()

                await websocket.send_json(
                    {"error": str(e)}
                )
    except WebSocketDisconnect:
        pass

@app.post("/reset-memory")
async def reset_conversation():
    """Reset the conversation state. It deletes the two collections needed for keeping LangGraph state in MongoDB.
    
    Raises:
        HTTPException: If there is an error resetting the conversation state.
    Returns:
        dict: A dictionary containing the result of the reset operation.
    """
    try:
        result = await reset_conversation_state()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
