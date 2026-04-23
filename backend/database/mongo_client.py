from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None

def init_db(app):
    global _client, _db
    try:
        _client = MongoClient(app.config['MONGO_URI'], serverSelectionTimeoutMS=5000)
        _client.admin.command('ping')
        _db = _client.get_default_database()
        logger.info("MongoDB connected successfully")
        _create_indexes()
    except ConnectionFailure as e:
        logger.warning(f"MongoDB unavailable, using in-memory fallback: {e}")
        _db = None

def _create_indexes():
    if _db is None:
        return
    try:
        _db.products.create_index([("name", "text"), ("description", "text"), ("category", "text")])
        _db.products.create_index("platform")
        _db.products.create_index("category")
        _db.products.create_index("price")
        _db.conversations.create_index("session_id")
        _db.search_logs.create_index("timestamp")
        logger.info("MongoDB indexes created")
    except Exception as e:
        logger.error(f"Index creation error: {e}")

def get_db():
    return _db

def is_connected():
    return _db is not None