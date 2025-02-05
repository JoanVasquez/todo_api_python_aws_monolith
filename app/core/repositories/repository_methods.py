from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from utils.cache_util_model import CacheModel

# Declare a generic type variable
T = TypeVar("T")


class IRepository(ABC, Generic[T]):

    @abstractmethod
    async def create_entity(
            self,
            entity: T,
            cache_model: Optional[CacheModel] = None) -> Optional[T]:
        """
        Create an entity in the repository.

        :param entity: The entity to create.
        :param cache_model: Optional cache configuration.
        :return: The created entity or None.
        """

    @abstractmethod
    async def find_entity_by_id(
            self,
            id: int,
            cache_model: Optional[CacheModel] = None) -> Optional[T]:
        """
        Find an entity by its ID.

        :param id: The identifier of the entity.
        :param cache_model: Optional cache configuration.
        :return: The found entity or None.
        """

    @abstractmethod
    async def update_entity(
        self,
        id: int,
        updated_data: Dict[str, Any],
        cache_model: Optional[CacheModel] = None,
    ) -> Optional[T]:
        """
        Update an entity with new data.

        :param id: The identifier of the entity to update.
        :param updated_data: A dictionary containing the updated fields.
        :param cache_model: Optional cache configuration.
        :return: The updated entity or None.
        """

    @abstractmethod
    async def delete_entity(self,
                            id: int,
                            cache_model: Optional[CacheModel] = None) -> bool:
        """
        Delete an entity by its ID.

        :param id: The identifier of the entity.
        :param cache_model: Optional cache configuration.
        :return: True if deletion was successful, False otherwise.
        """

    @abstractmethod
    async def get_all_entities(self,
                               cache_model: Optional[CacheModel] = None
                               ) -> List[T]:
        """
        Retrieve all entities.

        :param cache_model: Optional cache configuration.
        :return: A list of all entities.
        """

    @abstractmethod
    async def get_entities_with_pagination(
        self,
        skip: int,
        take: int,
        cache_model: Optional[CacheModel] = None
    ) -> Dict[str, Union[List[T], int]]:
        """
        Retrieve entities with pagination.

        :param skip: The number of entities to skip.
        :param take: The number of entities to retrieve.
        :param cache_model: Optional cache configuration.
        :return: A dictionary with:
                 - 'data': List of entities,
                 - 'count': Total number of entities available.
        """
