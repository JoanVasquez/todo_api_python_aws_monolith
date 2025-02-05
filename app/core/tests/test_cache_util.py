import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from core.utils.cache_util import Cache, init_cache


class TestCacheUtil(unittest.IsolatedAsyncioTestCase):

    async def test_set_success(self):
        # Create a fake Redis client with an async set method.
        fake_client = MagicMock()
        fake_client.set = AsyncMock(return_value=True)
        cache_instance = Cache(fake_client)
        await cache_instance.set("test_key", "test_value", 60)
        fake_client.set.assert_called_once_with("test_key",
                                                "test_value",
                                                ex=60)

    async def test_get_success(self):
        # Create a fake Redis client with an async get returning bytes.
        fake_client = MagicMock()
        fake_client.get = AsyncMock(return_value=b"test_value")
        cache_instance = Cache(fake_client)
        result = await cache_instance.get("test_key")
        self.assertEqual(result, "test_value")
        fake_client.get.assert_called_once_with("test_key")

    async def test_get_returns_none(self):
        # Create a fake Redis client with an async get returning None.
        fake_client = MagicMock()
        fake_client.get = AsyncMock(return_value=None)
        cache_instance = Cache(fake_client)
        result = await cache_instance.get("test_key")
        self.assertIsNone(result)
        fake_client.get.assert_called_once_with("test_key")

    async def test_delete_success(self):
        # Create a fake Redis client with an async delete method.
        fake_client = MagicMock()
        fake_client.delete = AsyncMock(return_value=True)
        cache_instance = Cache(fake_client)
        await cache_instance.delete("test_key")
        fake_client.delete.assert_called_once_with("test_key")

    @patch("core.utils.cache_util.get_cached_parameter")
    @patch("core.utils.cache_util.redis.Redis.from_url")
    async def test_init_cache_success(self, mock_from_url,
                                      mock_get_cached_parameter):
        # Simulate environment: get_cached_parameter returns a fake URL.
        mock_get_cached_parameter.return_value = "redis://redis:6379"
        # Create a fake Redis client with async ping.
        fake_client = MagicMock()
        fake_client.ping = AsyncMock(return_value=True)
        mock_from_url.return_value = fake_client

        cache_obj = await init_cache()
        self.assertIsInstance(cache_obj, Cache)
        fake_client.ping.assert_called_once()
        mock_from_url.assert_called_once_with("redis://redis:6379")

    @patch("core.utils.cache_util.get_cached_parameter")
    @patch("core.utils.cache_util.redis.Redis.from_url")
    async def test_init_cache_failure(self, mock_from_url,
                                      mock_get_cached_parameter):
        # Simulate environment: get_cached_parameter returns a fake URL.
        mock_get_cached_parameter.return_value = "redis://redis:6379"
        # Create a fake Redis client where ping raises an exception.
        fake_client = MagicMock()
        fake_client.ping = AsyncMock(side_effect=Exception("Ping failed"))
        mock_from_url.return_value = fake_client

        with self.assertRaises(Exception) as context:
            await init_cache()
        self.assertIn("Failed to initialize Redis client",
                      str(context.exception))

    async def test_local_env_missing_redis_url(self):
        # Ensure that in a local environment with no REDIS_URL,
        # an exception is raised.
        # Use clear=True to remove any preexisting environment variables.
        with patch.dict(os.environ, {"DJANGO_ENV": "local"}, clear=True):
            with self.assertRaises(Exception) as context:
                await init_cache()
            self.assertIn("Environment variable 'REDIS_URL' is not set",
                          str(context.exception))
