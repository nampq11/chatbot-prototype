from sentence_transformers import SentenceTransformer
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers import (
    MongoDBAtlasHybridSearchRetriever,
)

from loguru import logger

from src.config import Config

from .embeddings import get_embedding_model

Retriever = MongoDBAtlasHybridSearchRetriever

config = Config()

def get_retriever(
    embedding_model_id: str,
    k: int = 3,
    namespace: str = config.mongo.COSMETIC_SURGEON_COLLECTION,
    text_key: str = "text",
    search_index_name: str = config.mongo.COSMETIC_SURGEON_SEARCH_INDEX_NAME,
    device: str = "cpu"
) -> Retriever:
    logger.info(
        f"Initializing retriever | model: {embedding_model_id} | device: {device} | top_k: {k}"
    )
    
    embedding_model = get_embedding_model(
        embedding_model_id,
        device
    )
    return get_hybird_search_retriever(
        embedding_model=embedding_model,
        k=k,
        namespace=namespace,
        text_key=text_key,
        search_index_name=search_index_name,
    )

def get_hybird_search_retriever(
    embedding_model: SentenceTransformer,
    k: int = 3,
    namespace: str = config.mongo.COSMETIC_SURGEON_COLLECTION,
    text_key: str = "text",
    search_index_name: str = config.mongo.COSMETIC_SURGEON_SEARCH_INDEX_NAME,
) -> Retriever:
    """Get a hybrid search retriever."""
    vector_store = MongoDBAtlasVectorSearch(
        connection_string=config.mongo.URI,
        namespace=namespace,
        embedding=embedding_model,
        text_key=text_key,
        index_name=config.mongo.COSMETIC_SURGEON_VECTOR_STORE
    )
    
    return MongoDBAtlasHybridSearchRetriever(
        vectorstore=vector_store,
        search_index_name=search_index_name,
        k=k
    )