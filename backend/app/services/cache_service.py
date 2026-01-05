"""
Redis caching service for performance optimization.
"""

import json
import logging
from typing import Optional, Any, List
import redis
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service for application data."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.cache_ttl = int(os.getenv("CACHE_TTL", 300))  # 5 minutes default
        
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection."""
        try:
            redis_password = os.getenv("REDIS_PASSWORD")
            redis_use_ssl = os.getenv("REDIS_USE_SSL", "false").lower() == "true"
            
            self.client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=redis_password if redis_password else None,
                ssl=redis_use_ssl,
                ssl_cert_reqs="required" if redis_use_ssl else None,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info("Redis connection established: %s:%d", self.redis_host, self.redis_port)
        except Exception as e:
            logger.warning("Redis connection failed: %s. Caching disabled.", e)
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/error
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                logger.info("Cache HIT: %s", key)
                return json.loads(value)
            logger.info("Cache MISS: %s", key)
            return None
        except Exception as e:
            logger.error("Cache get error: %s", e)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: CACHE_TTL from env)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            ttl = ttl or self.cache_ttl
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            logger.info("Cache SET: %s (TTL: %ds)", key, ttl)
            return True
        except Exception as e:
            logger.error("Cache set error: %s", e)
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            logger.info("Cache DELETE: %s", key)
            return True
        except Exception as e:
            logger.error("Cache delete error: %s", e)
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., "documents:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info("Cache CLEAR: %s (%d keys)", pattern, deleted)
                return deleted
            return 0
        except Exception as e:
            logger.error("Cache clear error: %s", e)
            return 0
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False


# Global cache instance
cache_service = CacheService()
