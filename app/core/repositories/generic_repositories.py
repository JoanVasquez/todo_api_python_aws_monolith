import json
from abc import ABC
from typing import Any, Dict, List, Optional, Type, TypeVar

from django.forms.models import model_to_dict

from core.utils.cache_util import cache
from core.utils.cache_util_model import CacheModel
from core.utils.logger import get_logger
from core.utils.model_serializers import deserialize_instance

logger = get_logger(__name__)

T = TypeVar("T")


class GenericRepository(ABC):
    """
    A generic repository for Django models.
    Concrete repositories should inherit from this class.
    """

    def __init__(self, model: Type[T]) -> None:
        self.model = model

    def create_entity(self,
                      entity: T,
                      cache_model: Optional[CacheModel] = None) -> Optional[T]:
        try:
            entity.save()
            if cache_model:
                data = json.dumps(model_to_dict(entity))
                cache.set(cache_model.key,
                          data,
                          timeout=cache_model.expiration)
            return entity
        except Exception as error:
            logger.error("[GenericRepository] Error creating entity: %s",
                         error,
                         exc_info=True)
            return None

    def find_entity_by_id(
            self,
            id: int,
            cache_model: Optional[CacheModel] = None) -> Optional[T]:
        try:
            if cache_model:
                cached = cache.get(cache_model.key)
                if cached:
                    data = json.loads(cached)
                    return deserialize_instance(self.model, data)
            entity = self.model.objects.filter(pk=id).first()
            if not entity:
                logger.info("[GenericRepository] Entity with id %s not found",
                            id)
                raise Exception("Entity not found")
            if cache_model:
                data = json.dumps(model_to_dict(entity))
                cache.set(cache_model.key,
                          data,
                          timeout=cache_model.expiration)
            return entity
        except Exception as error:
            logger.error("[GenericRepository] Error finding entity: %s",
                         error,
                         exc_info=True)
            return None

    def update_entity(
        self,
        id: int,
        updated_data: Dict[str, Any],
        cache_model: Optional[CacheModel] = None,
    ) -> Optional[T]:
        try:
            updated = self.model.objects.filter(pk=id).update(**updated_data)
            if not updated:
                logger.error(
                    "[GenericRepository] Entity with id %s not found for "
                    "update", id)
                raise Exception(f"Entity with id {id} not found")
            updated_entity = self.find_entity_by_id(id)
            if not updated_entity:
                logger.error(
                    "[GenericRepository] Updated entity with id %s not found",
                    id)
                raise Exception(f"Entity with id {id} not found")
            if cache_model:
                data = json.dumps(model_to_dict(updated_entity))
                cache.set(cache_model.key,
                          data,
                          timeout=cache_model.expiration)
            return updated_entity
        except Exception as error:
            logger.error("[GenericRepository] Error updating entity: %s",
                         error,
                         exc_info=True)
            return None

    def delete_entity(self,
                      id: int,
                      cache_model: Optional[CacheModel] = None) -> bool:
        try:
            result = self.model.objects.filter(pk=id).delete()
            if result[0] == 0:
                logger.error(
                    "[GenericRepository] Failed to delete entity with id %s",
                    id)
                raise Exception(f"Entity with id {id} not found")
            if cache_model:
                cache.delete(cache_model.key)
            return True
        except Exception as error:
            logger.error("[GenericRepository] Error deleting entity: %s",
                         error,
                         exc_info=True)
            return False

    def get_all_entities(self,
                         cache_model: Optional[CacheModel] = None) -> List[T]:
        try:
            if cache_model:
                cached = cache.get(cache_model.key)
                if cached:
                    data_list = json.loads(cached)
                    return [
                        deserialize_instance(self.model, data)
                        for data in data_list
                    ]
            entities = list(self.model.objects.all())
            if cache_model:
                data_list = [model_to_dict(e) for e in entities]
                cache.set(
                    cache_model.key,
                    json.dumps(data_list),
                    timeout=cache_model.expiration,
                )
            return entities
        except Exception as error:
            logger.error(
                "[GenericRepository] Error retrieving all entities: %s",
                error,
                exc_info=True,
            )
            return []

    def get_entities_with_pagination(
            self,
            skip: int,
            take: int,
            cache_model: Optional[CacheModel] = None) -> Dict[str, Any]:
        try:
            if cache_model:
                cached = cache.get(cache_model.key)
                if cached:
                    return json.loads(cached)
            qs = self.model.objects.all()
            count = qs.count()
            data = list(qs[skip:skip + take])
            result = {"data": data, "count": count}
            if cache_model:
                serializable_data = [model_to_dict(e) for e in data]
                cache_data = json.dumps({
                    "data": serializable_data,
                    "count": count
                })
                cache.set(cache_model.key,
                          cache_data,
                          timeout=cache_model.expiration)
            return result
        except Exception as error:
            logger.error("[GenericRepository] Error in pagination: %s",
                         error,
                         exc_info=True)
            return {"data": [], "count": 0}
