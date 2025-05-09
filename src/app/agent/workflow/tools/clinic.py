from src.app.agent.workflow.tools.base import config, create_retriever_tool, get_retriever
from src.config import Config

config = Config()

def get_clinic_retriever():
    return get_retriever(
        k=config.rag.TOP_K,
        namespace=f"{config.mongo.DB_NAME}.{config.mongo.COSMETIC_SURGEON_COLLECTION}",
        text_key="text",
        search_index_name=config.mongo.COSMETIC_SURGEON_SEARCH_INDEX_NAME,
    )

retriever_cosmetic_surgeon = get_clinic_retriever()

retriever_tool_cosmetic_surgeon = create_retriever_tool(
    retriever_cosmetic_surgeon,
    "retriever_cosmetic_surgeon",
    "Retrieve information about doctor, clinic, hospital, etc.",
    response_format="content_and_artifact"
)
