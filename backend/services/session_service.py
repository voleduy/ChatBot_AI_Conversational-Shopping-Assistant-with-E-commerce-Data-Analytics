
from datetime import datetime
from database.mongo_client import get_db
import logging

logger = logging.getLogger(__name__)

_memory_sessions = {}
_memory_logs = []

def get_session_history(session_id: str) -> list:
    db = get_db()
    if db is not None:
        try:
            doc = db.conversations.find_one({"session_id": session_id})
            if doc:
                return doc.get("messages", [])
        except Exception as e:
            logger.error(f"Session fetch error: {e}")
    return _memory_sessions.get(session_id, {}).get("messages", [])

def save_message(session_id: str, role: str, content: str):
    msg = {"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()}
    db = get_db()
    if db is not None:
        try:
            db.conversations.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": msg},
                    "$set": {"last_active": datetime.utcnow()},
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
            return
        except Exception as e:
            logger.error(f"Save message error: {e}")
    
    if session_id not in _memory_sessions:
        _memory_sessions[session_id] = {"messages": [], "preferences": {}}
    _memory_sessions[session_id]["messages"].append(msg)

def get_user_preferences(session_id: str) -> dict:
    db = get_db()
    if db is not None:
        try:
            doc = db.conversations.find_one({"session_id": session_id})
            if doc:
                return doc.get("preferences", {})
        except Exception:
            pass
    return _memory_sessions.get(session_id, {}).get("preferences", {})

def update_user_preferences(session_id: str, preferences: dict):
    db = get_db()
    if db is not None:
        try:
            db.conversations.update_one(
                {"session_id": session_id},
                {"$set": {"preferences": preferences}},
                upsert=True
            )
            return
        except Exception as e:
            logger.error(f"Update prefs error: {e}")
    if session_id not in _memory_sessions:
        _memory_sessions[session_id] = {"messages": [], "preferences": {}}
    _memory_sessions[session_id]["preferences"].update(preferences)

def log_search(session_id: str, query: str, categories: list, price_max: int, result_count: int):
    log_entry = {
        "session_id": session_id,
        "query": query,
        "categories": categories,
        "price_max": price_max,
        "result_count": result_count,
        "timestamp": datetime.utcnow()
    }
    db = get_db()
    if db is not None:
        try:
            db.search_logs.insert_one(log_entry)
            return
        except Exception as e:
            logger.error(f"Search log error: {e}")
    _memory_logs.append(log_entry)

def get_analytics_data() -> dict:
    db = get_db()
    
    try:
        if db is not None:
            pipeline_cat = [
                {"$unwind": "$categories"},
                {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            top_cats = list(db.search_logs.aggregate(pipeline_cat))

            pipeline_price = [
                {"$match": {"price_max": {"$gt": 0}}},
                {"$bucket": {
                    "groupBy": "$price_max",
                    "boundaries": [0, 500000, 2000000, 5000000, 10000000, 20000000, 100000000],
                    "default": "other",
                    "output": {"count": {"$sum": 1}}
                }}
            ]
            price_dist = list(db.search_logs.aggregate(pipeline_price))
            
            total_searches = db.search_logs.count_documents({})
            
            return {
                "total_searches": total_searches,
                "top_categories": top_cats,
                "price_distribution": price_dist,
                "source": "mongodb"
            }
    except Exception as e:
        logger.error(f"Analytics error: {e}")

    from collections import Counter
    cats = Counter()
    prices = []
    for log in _memory_logs:
        for c in log.get("categories", []):
            cats[c] += 1
        if log.get("price_max"):
            prices.append(log["price_max"])
    
    return {
        "total_searches": len(_memory_logs),
        "top_categories": [{"_id": k, "count": v} for k, v in cats.most_common(10)],
        "price_distribution": _bucket_prices(prices),
        "source": "memory"
    }

def _bucket_prices(prices: list) -> list:
    buckets = [
        (0, 500000, "Dưới 500k"),
        (500000, 2000000, "500k - 2tr"),
        (2000000, 5000000, "2tr - 5tr"),
        (5000000, 10000000, "5tr - 10tr"),
        (10000000, 20000000, "10tr - 20tr"),
        (20000000, float('inf'), "Trên 20tr"),
    ]
    result = []
    for lo, hi, label in buckets:
        count = sum(1 for p in prices if lo <= p < hi)
        if count > 0:
            result.append({"_id": label, "count": count})
    return result