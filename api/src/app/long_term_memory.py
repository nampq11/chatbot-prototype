from langchain_core.documents import Document
from loguru import logger

from src.app.data.deduplicate_documents import deduplicate_documents
from src.app.rag.retrieval import Retriever, get_retriever
from src.app.rag.splitter import Splitter, get_splitter
from src.config import settings
from src.infastructure.mogo import MongoClientWrapper, MongoIndex

class LongTermMemoryCreator:
    def __init__(self, retriever: Retriever, splitter: Splitter):
        self.retriever = retriever
        self.splitter = splitter
        
    @classmethod
    def build_from_settings(cls) -> "LongTermMemoryCreator":
        retriever = get_retriever(
            embedding_model_id=settings.TEXT_EMBEDDING_MODEL_ID,
            k=settings.TOP_K,
            device=settings.DEVICE,
        )
        splitter = get_splitter(chunk_size=settings.CHUNK_SIZE)

        return cls(retriever=retriever, splitter=splitter)
    
    def __call__(self) -> None:
        with MongoClientWrapper(
            model=Document,
            collection_name=settings.LONG_TERM_MEMORY_COLLECTION
        ) as client:
            client.clear_collection()
        
        
class LongTermMemoryRetriever:
    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    @classmethod
    def build_from_settings(cls) -> "LongTermMemoryRetriever":
        retriever = get_retriever(
            embedding_model_id=settings.TEXT_EMBEDDING_MODEL_ID,
            k=settings.TOP_K,
            device=settings.DEVICE,
        )
        return cls(retriever=retriever)

    def __call__(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)
        