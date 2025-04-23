from langchain.tools.retriever import create_retriever_tool

from src.rag.retrieval import get_retriever
from src.config import Config

retriever = get_retriever(
    embedding_model_id=Config.RAG_TEXT_EMBEDDING_MODEL_ID,
    k=Config.RAG_TOP_K,
    device=Config.RAG_DEVICE,
)

retriever_tool = create_retriever_tool(
    retriever,
    "retriever_bookingcare_contenxt",
    "Search and return information about specific topics. Always use this tool when the user asks about a document, article of BookingCare.",
)

tools = [retriever_tool]