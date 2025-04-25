from typing import Generic, Type, TypeVar

from bson import ObjectId
from pydantic import BaseModel
from pymongo import MongoClient, errors
from src.config import Config
from loguru import logger

T = TypeVar("T", bound=BaseModel)

config = Config()

class MongoClientWrapper(Generic[T]):
    def __init__(
        self,
        model: Type[T],
        collection_name: str,
        database_name: str = config.MONGO_DB_NAME,
        mogodb_uri: str = config.MONGO_URI,
    ):
        self.model = model
        self.collection_name = collection_name
        self.database_name = database_name
        self.mogodb_uri = mogodb_uri

        try:
            self.client = MongoClient(mogodb_uri, appname="bkcare")
            self.client.admin.command("ping")
        except Exception as e:
            raise ConnectionError(f"Could not connect to MongoDB: {e}")

        self.database = self.client[database_name]
        self.collection = self.database[collection_name]
        logger.info(
            f"Connected to MongoDB instance:\n URI: {mogodb_uri}\n Database: {database_name}\n Collection: {collection_name}"
        )

    def __enter__(self) -> "MongoClientWrapper":
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.close()
    
    def clear_collection(self) -> None:
        try:
            result = self.collection.delete_many({})
            logger.debug(
                f"Cleared collection. Deleted {result.deleted_count} documents."
            )
        except errors.PyMongoError as e:
            logger.error(f"Error clearing collection: {e}")
            raise
    
    def ingest_documents(self, documents: list[T]) -> None:
        try:
            if not documents or not all(
                isinstance(doc, BaseModel) for doc in documents
            ):
                raise ValueError("Documents must be a list of Pydantic models.")
            
            dict_documents = [doc.model_dump() for doc in documents]

            for doc in dict_documents:
                doc.pop("_id", None)
            
            self.collection.insert_many(dict_documents)
            logger.debug(
                f"Inserted {len(dict_documents)} documents into MongoDB."
            )

        except errors.PyMongoError as e:
            logger.error(f"Error inserting documents: {e}")
            raise
    
    def fetch_documents(self, limit: int, query: dict) -> list[T]:
        try:
            documents = list(self.collection.find(query).limit(limit=limit))
            logger.debug(
                f"Fetched {len(documents)} documents from MongoDB with query: {query}"
            )
            return self.__parse_documents(documents)
        except errors.PyMongoError as e:
            logger.error(f"Error fetching documents: {e}")
            raise

    def __parse_documents(self, documents: list[dict]) -> list[T]:
        parsed_documents = []
        for doc in documents:
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
            
            _id = doc.pop("_id", None)
            doc['id'] = _id

            parsed_doc = self.model.model_validate(doc)
            parsed_documents.append(parsed_doc)
        
        return parsed_documents
    
    def get_collection_count(self) -> int:
        try:
            return self.collection.count_documents({})
        except errors.PyMongoError as e:
            logger.error(f"Error getting collection count: {e}")
            raise
    
    def close(self) -> None:
        self.client.close()
        logger.debug("Closed MongoDB connection.")
