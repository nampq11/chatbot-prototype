from src.app.agent.workflow.tools.base import config, create_retriever_tool, get_retriever
from src.config import Config

config = Config()

retriever_memory = get_retriever(
    embedding_model_id=config.rag.TEXT_EMBEDDING_MODEL_ID,
    k=config.rag.TOP_K,
    device=config.rag.DEVICE,
    namespace=f"{config.mongo.DB_NAME}.{config.mongo.LONG_TERM_MEMORY_COLLECTION}",
    text_key="text",
    search_index_name=config.mongo.LONG_TERM_MEMORY_SEARCH_INDEX_NAME,
)

retriever_tool = create_retriever_tool(
    retriever_memory,
    "retriever_memory",
    "Retrieve information from the long-term memory"
)

def get_memory_retriever():
    return get_retriever(
        embedding_model_id=config.rag.TEXT_EMBEDDING_MODEL_ID,
        k=config.rag.TOP_K,
        device=config.rag.DEVICE,
        namespace=f"{config.mongo.DB_NAME}.{config.mongo.LONG_TERM_MEMORY_COLLECTION}",
        text_key="text",
        search_index_name=config.mongo.LONG_TERM_MEMORY_SEARCH_INDEX_NAME,
    )
