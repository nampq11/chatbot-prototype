from src.app.agent.workflow.tools.base import config, create_retriever_tool, get_retriever
from src.config import settings

retriever_memory = get_retriever(
    k=settings.TOP_K,
    namespace=f"{settings.DB_NAME}.{settings.LONG_TERM_MEMORY_COLLECTION}",
    text_key="text",
    search_index_name=settings.LONG_TERM_MEMORY_SEARCH_INDEX_NAME,
)

retriever_tool = create_retriever_tool(
    retriever_memory,
    "retriever_memory",
    "Retrieve information from the long-term memory"
)

def get_memory_retriever():
    return get_retriever(
        k=settings.TOP_K,
        namespace=f"{settings.DB_NAME}.{settings.LONG_TERM_MEMORY_COLLECTION}",
        text_key="text",
        search_index_name=settings.LONG_TERM_MEMORY_SEARCH_INDEX_NAME,
    )
