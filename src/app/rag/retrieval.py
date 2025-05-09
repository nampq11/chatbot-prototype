from sentence_transformers import SentenceTransformer
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.agents import tool

from langchain_mongodb.retrievers import (
    MongoDBAtlasHybridSearchRetriever,
)

from langchain_mongodb.retrievers.full_text_search import (
    MongoDBAtlasFullTextSearchRetriever,
)

from pymongo import MongoClient

from loguru import logger

from src.config import Config

from .embeddings import get_embedding_model

Retriever = MongoDBAtlasHybridSearchRetriever

config = Config()

client = MongoClient(config.mongo.URI)


logger.info(
    f"Initializing retriever | model: {config.rag.TEXT_EMBEDDING_MODEL_ID} | device: {config.rag.DEVICE} | top_k: {config.rag.TOP_K}"
)

embedding_model = get_embedding_model(
    model_id=config.rag.TEXT_EMBEDDING_MODEL_ID,
    device=config.rag.DEVICE
)

def get_retriever(
    k: int = 3,
    namespace: str = config.mongo.COSMETIC_SURGEON_COLLECTION,
    text_key: str = "text",
    search_index_name: str = config.mongo.COSMETIC_SURGEON_SEARCH_INDEX_NAME,
) -> Retriever:
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
    vector_store = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=config.mongo.URI,
        namespace=namespace,
        embedding=embedding_model,
        index_name=config.mongo.COSMETIC_SURGEON_VECTOR_STORE
    )
    
    return MongoDBAtlasHybridSearchRetriever(
        vectorstore=vector_store,
        search_index_name=search_index_name,
        k=k
    )

@tool
def vector_search(user_query: str) -> str:
    """
    Retrieve information using vector search to answer a user query.
    """

    vector_store = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=config.mongo.URI,
        namespace=f"{config.mongo.DB_NAME}.{config.mongo.COSMETIC_SURGEON_COLLECTION}",
        embedding=embedding_model,
        text_key="text",
        embedding_key="embedding",
        relevance_score_fn = "cosine"
    )

    retriever = vector_store.as_retriever(
        search_type = "similarity",
        search_kwargs = {
            "k": config.rag.TOP_K
        }
    )
    results = retriever.invoke(user_query)

    context = "\n\n".join([f"{doc.metadata}: {doc.page_content}" for doc in results])

    return context

@tool
def full_text_search(user_query: str) -> str:
    "Retrieve information based on text search"
    collection = client[config.mongo.DB_NAME][config.mongo.COSMETIC_SURGEON_COLLECTION]

    retriever = MongoDBAtlasFullTextSearchRetriever(
        collection=collection,
        search_field="text",
        search_index_name="search_index",
        top_k=config.rag.TOP_K
    )
    results = retriever.invoke(user_query)

    for doc in results:
        if doc:
            return doc.metadata
        else:
            return "No results found"
