import redis
import json
from app.core.logging import get_logger

logger = get_logger(__name__)
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


def _key(key: str) -> str:
    return f"rec:{key}"

def get_redis_client():
    return redis_client

def get(user_id: int):
    try:
        redis = get_redis_client()
        data = redis.get(_key(str(user_id)))
        return json.loads(data) if data else None
    except Exception as e:
        logger.warning(f"Redis get failed: {str(e)}")
        return None

def set(user_id: int, data: str, ttl: int = 300):
    try:
        redis = get_redis_client()
        redis.setex(_key(str(user_id)), ttl, json.dumps(data))
    except Exception as e:
        logger.warning(f"Redis set failed: {str(e)}")

def delete(key: str):
    redis_client.delete(_key(str(key)))
