import json
from typing import Optional

from django.forms.models import model_to_dict

from core.models import User
from core.repositories.generic_repositories import GenericRepository
from core.utils.cache_util import cache
from core.utils.cache_util_model import CacheModel
from core.utils.logger import get_logger
from core.utils.model_serializers import deserialize_instance

logger = get_logger(__name__)


class UserRepository(GenericRepository):

    def __init__(self) -> None:
        super().__init__(User)

    def find_user_by_username(
            self,
            username: str,
            cache_model: Optional[CacheModel] = None) -> Optional[User]:
        try:
            if cache_model:
                cache_entity = cache.get(cache_model.key)
                if cache_entity:
                    data = json.loads(cache_entity)
                    return deserialize_instance(self.model, data)
            user = self.model.objects.filter(username=username).first()
            if not user:
                logger.warning(
                    f"[UserRepository] No user found with username: {username}"
                )
                raise Exception(f"User with username {username} not found")
            if cache_model:
                data = json.dumps(model_to_dict(user))
                cache.set(cache_model.key,
                          data,
                          timeout=cache_model.expiration)
            return user
        except Exception:
            logger.error(
                "[UserRepository] Error finding user by username:",
                exc_info=True,
            )
            return None
