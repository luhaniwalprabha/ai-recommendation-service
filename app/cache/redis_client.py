import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get(key: str):
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None

def set(key: str, value, ttl: int = 3600):
    redis_client.set(key, json.dumps(value), ex=ttl)
