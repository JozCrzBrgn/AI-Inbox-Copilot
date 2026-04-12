import hashlib
import json

import redis
from fastapi.exceptions import HTTPException

from ..core.config import get_settings

# Configure redis client
cnf = get_settings()
redis_client = redis.Redis(
    host=cnf.redis.host,
    port=cnf.redis.port,
    db=cnf.redis.db,
    password=cnf.redis.password,
    decode_responses=True,
)


def _hash(text: str) -> str:
    """Hash the input text"""
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def _cache_get(key: str):
    """Get data from cache"""
    data = redis_client.get(key)
    return json.loads(data) if data else None


def _cache_set(key: str, value: dict, ttl=3600):
    """Set data in cache"""
    redis_client.set(key, json.dumps(value), ex=ttl)


def _check_token_budget(username: str, estimated_tokens: int, limit=10000):
    """Check token budget for user"""
    key = f"user:{username}:tokens"

    current = redis_client.get(key)
    current = int(current) if current else 0

    if current + estimated_tokens > limit:
        raise HTTPException(status_code=429, detail="Token budget exceeded")

    redis_client.incrby(key, estimated_tokens)
    redis_client.expire(key, 86400)


def _estimate_tokens(text: str) -> int:
    """Estimate tokens in text (1 token approximately 4 characters)"""
    return int(len(text) / 4)
