import redis
import json
from app.core.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
)

def get_redis_client():
    return redis_client

def get(key: str):
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.warning(f"Redis get failed for key={key}: {str(e)}")
        return None

def set(key: str, data, ttl: int = 300):
    try:
        redis_client.setex(key, ttl, json.dumps(data))
    except Exception as e:
        logger.warning(f"Redis set failed for key={key}: {str(e)}")

def delete(key: str):
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Redis delete failed for key={key}: {str(e)}")


def acquire_lock(key: str, ttl: int = 120) -> bool:
    try:
        return redis_client.set(key, "1", nx=True, ex=ttl) is True
    except Exception as e:
        logger.warning(f"Redis lock acquire failed for key={key}: {str(e)}")
        return True



