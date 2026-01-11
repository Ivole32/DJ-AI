"""
Redis handler utility.
Provides simple get/set helpers with JSON serialization.
"""


# Redis client
import redis

# Fast JSON serialization
import orjson

# Typing
from typing import Any, Optional


class RedisHandler:
    """
    Central Redis cache handler.
    """

    def __init__(self, host: str="localhost", port: int = 6379, db: int = 0, default_ttl: int = 600, enabled: bool = True):
        """
        Initialize Redis connection.

        Args:
            host (str): Redis host
            port (int): Redis port
            db (int): Redis database index
            default_ttl (int): Default TTL in seconds
            enabled (bool): Disable Redis without code changes
        """
        self.enabled = enabled
        self.default_ttl = default_ttl

        if not self.enabled:
            self.client = None
            return
        
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=False)

    def get(self, key: str) -> Optional[Any]:
        """
        Get and deserialize a value from Redis.
        Args:
            key (str): Redis key
        Returns:
            Optional[Any]: Deserialized value or None if not found
        """
        if not self.enabled:
            return None
        
        value = self.client.get(key)
        if value is None:
            return None
        
        try:
            return orjson.loads(value)
        except orjson.JSONDecodeError:
            return value
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Serialize and set a value in Redis with optional TTL.

        Args:
            key (str): Redis key
            value (Any): Value to serialize and store
            ttl (Optional[int]): Time-to-live in seconds
        """
        if not self.enabled:
            return
        
        ttl = ttl or self.default_ttl

        if isinstance(value, (dict, list)):
            value = orjson.dumps(value)

        self.client.setex(key, ttl, value)

    def delete(self, key: str) -> None:
        """
        Delete a key from Redis.

        Args:
            key (str): Redis key
        """
        if not self.enabled:
            return
        
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key (str): Redis key
        """
        if not self.enabled:
            return False
        
        return bool(self.client.exists(key))

    def flush(self) -> None:
        """
        Flush all keys in the current Redis database.
        """
        if not self.enabled:
            return
        
        self.client.flushdb()

    def make_key(self, *parts: str) -> str:
        """
        Create a standardized Redis key from parts.
        Args:
            parts (str): Parts to join into a key
        """
        return ":".join(str(p).strip().lower() for p in parts)