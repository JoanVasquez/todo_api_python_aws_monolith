import unittest
from unittest.mock import MagicMock

from core.repositories.generic_repositories import GenericRepository
from core.services.generic_service import GenericService
from core.utils.cache_util_model import CacheModel

# A dummy entity for testing


class DummyEntity:

    def __init__(self, id, data):
        self.id = id
        self.data = data

    def __eq__(self, other):
        return isinstance(
            other,
            DummyEntity) and self.id == other.id and self.data == other.data


class TestGenericService(unittest.TestCase):

    def setUp(self) -> None:
        # Create a mock repository instance.
        self.repo_mock = MagicMock(spec=GenericRepository)
        self.service = GenericService(self.repo_mock)
        self.cache_model = CacheModel(key="dummy_cache_key", expiration=100)
        self.dummy_entity = DummyEntity(1, "original data")

    def test_save(self):
        self.repo_mock.create_entity.return_value = self.dummy_entity
        result = self.service.save(self.dummy_entity, self.cache_model)
        self.repo_mock.create_entity.assert_called_once_with(
            self.dummy_entity, self.cache_model)
        self.assertEqual(result, self.dummy_entity)

    def test_find_by_id(self):
        self.repo_mock.find_entity_by_id.return_value = self.dummy_entity
        result = self.service.find_by_id(1, self.cache_model)
        self.repo_mock.find_entity_by_id.assert_called_once_with(
            1, self.cache_model)
        self.assertEqual(result, self.dummy_entity)

    def test_update(self):
        updated_data = {"data": "updated data"}
        updated_entity = DummyEntity(1, "updated data")
        self.repo_mock.update_entity.return_value = updated_entity
        result = self.service.update(1, updated_data, self.cache_model)
        self.repo_mock.update_entity.assert_called_once_with(
            1, updated_data, self.cache_model)
        self.assertEqual(result, updated_entity)

    def test_delete(self):
        self.repo_mock.delete_entity.return_value = True
        result = self.service.delete(1, self.cache_model)
        self.repo_mock.delete_entity.assert_called_once_with(
            1, self.cache_model)
        self.assertTrue(result)

    def test_find_all(self):
        entities = [self.dummy_entity]
        self.repo_mock.get_all_entities.return_value = entities
        result = self.service.find_all(self.cache_model)
        self.repo_mock.get_all_entities.assert_called_once_with(
            self.cache_model)
        self.assertEqual(result, entities)

    def test_find_with_pagination(self):
        paginated_result = {"data": [self.dummy_entity], "count": 1}
        self.repo_mock.get_entities_with_pagination.return_value = \
            paginated_result
        result = self.service.find_with_pagination(0, 10, self.cache_model)
        self.repo_mock.get_entities_with_pagination.assert_called_once_with(
            0, 10, self.cache_model)
        self.assertEqual(result, paginated_result)
