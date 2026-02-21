import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_redis_client():
    return redis_client

def get(key: str):
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None

def set(key: str, value, ttl: int = 3600):
    redis_client.set(key, json.dumps(value), ex=ttl)

def delete(key: str):
    redis_client.delete(key)

