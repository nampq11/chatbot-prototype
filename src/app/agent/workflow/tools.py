from langchain.tools.retriever import create_retriever_tool

from src.app.rag.retrieval import get_retriever
from src.config import Config

config = Config()

retriever = get_retriever(
    embedding_model_id=config.RAG_TEXT_EMBEDDING_MODEL_ID,
    k=config.RAG_TOP_K,
    device=config.RAG_DEVICE,
)

retriever_tool = create_retriever_tool(
    retriever,
    "retriever_bookingcare_contenxt",
    "Search and return information about specific topics. Always use this tool when the user asks about a document, article of BookingCare.",
)

tools = [retriever_tool]