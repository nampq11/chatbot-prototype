from loguru import logger
from pymongo import MongoClient

from src.config import Config

settings = Config()

async def reset_conversation_state() -> dict:
    try:
        client = MongoClient(settings.mongo.URI)
        db = client[settings.mongo.DB_NAME]

        collections_deleted = []

        if settings.mongo.STATE_CHECKPOINT_COLLECTION in db.list_collection_names():
            db.drop_collection(settings.mongo.STATE_CHECKPOINT_COLLECTION)
            collections_deleted.append(settings.mongo.STATE_CHECKPOINT_COLLECTION)
            logger.info(
                f"Deleted collection: {settings.mongo.STATE_CHECKPOINT_COLLECTION}"
            )
        
        if settings.mongo.STATE_WRITES_COLLECTION in db.list_collection_names():
            db.drop_collection(settings.mongo.STATE_WRITES_COLLECTION)
            collections_deleted.append(settings.mongo.STATE_WRITES_COLLECTION)
            logger.info(
                f"Deleted collection: {settings.mongo.STATE_WRITES_COLLECTION}"
            )
            
        client.close()

        if collections_deleted:
            return {
                "status": "success",
                "message": f"Successfully deleted collections: {', '.join(collections_deleted)}"
            }
        else:
            return {
                "status": "success",
                "message": "No collections need to be deleted"
            }
    except Exception as e:
        logger.error(f"Failed to reset conversation state: {str(e)}")
        raise Exception(f"Failed to reset conversation state: {str(e)}")