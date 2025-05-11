from loguru import logger
from pymongo import MongoClient

from src.config import settings

async def reset_conversation_state() -> dict:
    try:
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.DB_NAME]

        collections_deleted = []

        if settings.STATE_CHECKPOINT_COLLECTION in db.list_collection_names():
            db.drop_collection(settings.STATE_CHECKPOINT_COLLECTION)
            collections_deleted.append(settings.STATE_CHECKPOINT_COLLECTION)
            logger.info(
                f"Deleted collection: {settings.STATE_CHECKPOINT_COLLECTION}"
            )
        
        if settings.STATE_WRITES_COLLECTION in db.list_collection_names():
            db.drop_collection(settings.STATE_WRITES_COLLECTION)
            collections_deleted.append(settings.STATE_WRITES_COLLECTION)
            logger.info(
                f"Deleted collection: {settings.STATE_WRITES_COLLECTION}"
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