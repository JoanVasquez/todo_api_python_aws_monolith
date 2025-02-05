import os
from typing import Optional

import redis.asyncio as redis

from core.utils.logger import get_logger
from core.utils.ssm_util import get_cached_parameter

logger = get_logger(__name__)


class Cache:
    """
    A simple asynchronous cache interface wrapping Redis.
    """

    def __init__(self, client: redis.Redis):
        self.client = client

    async def set(self, key: str, value: str, ttl: int) -> None:
        """
        Set a key in Redis with an expiration (in seconds).
        """
        try:
            await self.client.set(key, value, ex=ttl)
        except Exception as e:
            logger.error(f"Redis set error for key '{key}': {e}",
                         exc_info=True)
            raise

    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from Redis. Returns None if the key does not exist.
        """
        try:
            value = await self.client.get(key)
            return value.decode("utf-8") if value is not None else None
        except Exception as e:
            logger.error(f"Redis get error for key '{key}': {e}",
                         exc_info=True)
            raise

    async def delete(self, key: str) -> None:
        """
        Delete a key from Redis.
        """
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error for key '{key}': {e}",
                         exc_info=True)
            raise


async def init_cache() -> Cache:
    """
    Initialize the Redis client using the URL from SSM (for production) or
    directly from an environment variable (for local/test) and return a Cache
    instance.
    """
    try:
        env = os.environ.get("DJANGO_ENV", "").lower()
        if env in ["local", "test"]:
            redis_url = os.environ.get("REDIS_URL")
            if not redis_url:
                raise Exception("Environment variable 'REDIS_URL' is not set")
            logger.info(f"[init_cache] Using local Redis URL: {redis_url}")
        else:
            # Retrieve the Redis URL using the SSM parameter name provided in
            # the environment variable REDIS_URL_SSM_NAME.
            param_name = os.environ["REDIS_URL_SSM_NAME"]
            redis_url = get_cached_parameter(param_name)
            logger.info(
                f"[init_cache] Fetched Redis URL from SSM for parameter: "
                f"{param_name}")
        client = redis.Redis.from_url(redis_url)
        # Optionally, check the connection with a PING.
        await client.ping()
        logger.info("Redis client initialized successfully")
        return Cache(client)
    except Exception as e:
        logger.error(f"Failed to initialize Redis client: {e}", exc_info=True)
        raise Exception(f"Failed to initialize Redis client: {e}") from e


# Global variable for the cache instance
cache: Cache = None  # type: ignore


async def _initialize_cache():
    """
    Asynchronously initialize the global cache.
    """
    global cache
    cache = await init_cache()
