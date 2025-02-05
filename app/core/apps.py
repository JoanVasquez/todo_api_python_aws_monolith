import asyncio

from django.apps import AppConfig

from core.utils.cache_util import _initialize_cache


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        try:
            # Try to get the running event loop (if one exists)
            loop = asyncio.get_running_loop()
            # Schedule the async cache initialization
            loop.create_task(_initialize_cache())
        except RuntimeError:
            # If no running loop, create one and run the initializer
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_initialize_cache())
