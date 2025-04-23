from sentence_transformers import SentenceTransformer
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers import (
    MongoDBAtlasHybridSearchRetriever,
)

from loguru import logger

from src.config import Config

from .embeddings import get_embedding_model

Retriever = MongoDBAtlasHybridSearchRetriever

def get_retriever(
    embedding_model_id: str,
    k: int = 3,
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
        k=k
    )

def get_hybird_search_retriever(
    embedding_model: SentenceTransformer,
    k: int
) -> MongoDBAtlasHybridSearchRetriever:
    
    vectorstore = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=Config.MONGO_URI,
        embedding=embedding_model,
        namespace=f"{Config.MONGO_DB_NAME}.{Config.MONGO_LONG_TERM_MEMORY_COLLECTION}",
        text_key="chunk",
        embedding_key="embedding",
        relevance_score_fn="consine",
    )

    retriever = MongoDBAtlasHybridSearchRetriever(
        vectorstore=vectorstore,
        search_index_name="hybrid_search_index",
        top_k=k,
        vector_penalty=50,
        fulltext_penalty=50,
    )
    return retriever