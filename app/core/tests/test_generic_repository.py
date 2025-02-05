import json
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

# Import the repository and CacheModel from the correct module path.
from core.repositories.generic_repositories import GenericRepository
from core.utils.cache_util_model import CacheModel


# --- Helper: FakeQuerySet ---
class FakeQuerySet(list):

    def count(self):
        return len(self)


# --- Dummy Model and Repository ---


class DummyModel:
    # Simulate the Django ORM manager with a MagicMock.
    objects = MagicMock()

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def save(self):
        # In a real model, this would save the instance to the DB.
        pass


# A concrete repository for DummyModel.
class DummyRepository(GenericRepository):

    def __init__(self):
        super().__init__(DummyModel)


# --- Unit Tests ---


class TestGenericRepository(unittest.TestCase):

    def setUp(self) -> None:
        # Reset the DummyModel manager mock before each test.
        DummyModel.objects.reset_mock()
        self.repo = DummyRepository()
        self.test_entity = DummyModel(1, "Test Name")
        self.test_entity_dict = {"id": 1, "name": "Test Name"}
        self.cache_key = "dummy_key"
        self.cache_model = CacheModel(key=self.cache_key, expiration=300)

    # --- Tests for create_entity ---

    @patch("core.repositories.generic_repositories.cache")
    @patch("core.repositories.generic_repositories.model_to_dict")
    def test_create_entity_success(self, mock_model_to_dict, mock_cache):
        # Arrange: configure model_to_dict to return our test_entity_dict.
        mock_model_to_dict.return_value = self.test_entity_dict

        # Act
        result = self.repo.create_entity(self.test_entity, self.cache_model)

        # Assert
        self.assertEqual(result, self.test_entity)
        expected_data = json.dumps(self.test_entity_dict)
        mock_cache.set.assert_called_once_with(self.cache_key,
                                               expected_data,
                                               timeout=300)

    @patch("core.repositories.generic_repositories.logger")
    def test_create_entity_failure(self, mock_logger):
        # Arrange: simulate an exception during save.
        def fake_save():
            raise Exception("save failed")

        self.test_entity.save = fake_save

        # Act
        result = self.repo.create_entity(self.test_entity, self.cache_model)

        # Assert
        self.assertIsNone(result)
        mock_logger.error.assert_called()  # verify that error was logged

    # --- Tests for find_entity_by_id ---

    @patch("core.repositories.generic_repositories.cache")
    @patch("core.repositories.generic_repositories.deserialize_instance")
    def test_find_entity_by_id_cache_hit(self, mock_deserialize_instance,
                                         mock_cache):
        # Arrange: simulate a cache hit.
        cached_json = json.dumps(self.test_entity_dict)
        mock_cache.get.return_value = cached_json
        mock_deserialize_instance.return_value = self.test_entity

        # Act
        result = self.repo.find_entity_by_id(1, self.cache_model)

        # Assert
        self.assertEqual(result, self.test_entity)
        mock_cache.get.assert_called_once_with(self.cache_key)
        mock_deserialize_instance.assert_called_once_with(
            DummyModel, self.test_entity_dict)

    @patch("core.repositories.generic_repositories.cache")
    @patch("core.repositories.generic_repositories.model_to_dict")
    def test_find_entity_by_id_no_cache_found(self, mock_model_to_dict,
                                              mock_cache):
        # Arrange: simulate cache miss.
        mock_cache.get.return_value = None
        # Simulate the ORM returning our entity.
        DummyModel.objects.filter.return_value.first.return_value = (
            self.test_entity)
        mock_model_to_dict.return_value = self.test_entity_dict

        # Act
        result = self.repo.find_entity_by_id(1, self.cache_model)

        # Assert
        self.assertEqual(result, self.test_entity)
        DummyModel.objects.filter.assert_called_with(pk=1)
        expected_data = json.dumps(self.test_entity_dict)
        mock_cache.set.assert_called_once_with(self.cache_key,
                                               expected_data,
                                               timeout=300)

    @patch("core.repositories.generic_repositories.cache")
    def test_find_entity_by_id_not_found(self, mock_cache):
        # Arrange: simulate cache miss and no matching entity.
        mock_cache.get.return_value = None
        DummyModel.objects.filter.return_value.first.return_value = None

        # Act
        result = self.repo.find_entity_by_id(999, self.cache_model)

        # Assert: should return None if entity not found.
        self.assertIsNone(result)

    # --- Tests for update_entity ---

    @patch("core.repositories.generic_repositories.cache")
    @patch("core.repositories.generic_repositories.model_to_dict")
    @patch("core.repositories.generic_repositories."
           "GenericRepository.find_entity_by_id")
    def test_update_entity_success(self, mock_find_entity_by_id,
                                   mock_model_to_dict, mock_cache):
        # Arrange:
        updated_data: Dict[str, Any] = {"name": "Updated Name"}
        DummyModel.objects.filter.return_value.update.return_value = 1
        updated_entity = DummyModel(1, "Updated Name")
        mock_find_entity_by_id.return_value = updated_entity
        # Patch model_to_dict to simulate Django's model_to_dict output.
        mock_model_to_dict.return_value = {"id": 1, "name": "Updated Name"}

        # Act
        result = self.repo.update_entity(1, updated_data, self.cache_model)

        # Assert
        self.assertEqual(result, updated_entity)
        DummyModel.objects.filter.assert_called_with(pk=1)
        DummyModel.objects.filter.return_value.update.assert_called_with(
            **updated_data)
        expected_data = json.dumps({"id": 1, "name": "Updated Name"})
        mock_cache.set.assert_called_once_with(self.cache_key,
                                               expected_data,
                                               timeout=300)

    @patch("core.repositories.generic_repositories.cache")
    def test_update_entity_not_found(self, mock_cache):
        # Arrange: simulate no records updated.
        DummyModel.objects.filter.return_value.update.return_value = 0

        # Act
        result = self.repo.update_entity(999, {"name": "Does not matter"},
                                         self.cache_model)

        # Assert
        self.assertIsNone(result)

    # --- Tests for delete_entity ---

    @patch("core.repositories.generic_repositories.cache")
    def test_delete_entity_success(self, mock_cache):
        # Arrange: simulate a successful deletion.
        DummyModel.objects.filter.return_value.delete.return_value = (1, {})

        # Act
        result = self.repo.delete_entity(1, self.cache_model)

        # Assert
        self.assertTrue(result)
        DummyModel.objects.filter.assert_called_with(pk=1)
        DummyModel.objects.filter.return_value.delete.assert_called_once()
        mock_cache.delete.assert_called_once_with(self.cache_key)

    @patch("core.repositories.generic_repositories.cache")
    def test_delete_entity_failure(self, mock_cache):
        # Arrange: simulate deletion failure (nothing deleted).
        DummyModel.objects.filter.return_value.delete.return_value = (0, {})

        # Act
        result = self.repo.delete_entity(999, self.cache_model)

        # Assert
        self.assertFalse(result)

    # --- Tests for get_all_entities ---

    @patch("core.repositories.generic_repositories.cache")
    @patch("core.repositories.generic_repositories.deserialize_instance")
    def test_get_all_entities_cache_hit(self, mock_deserialize_instance,
                                        mock_cache):
        # Arrange: simulate cached list of entity dictionaries.
        cached_list = [self.test_entity_dict]
        mock_cache.get.return_value = json.dumps(cached_list)
        mock_deserialize_instance.return_value = self.test_entity

        # Act
        result = self.repo.get_all_entities(self.cache_model)

        # Assert
        self.assertEqual(result, [self.test_entity])
        mock_cache.get.assert_called_once_with(self.cache_key)
        mock_deserialize_instance.assert_called_once_with(
            DummyModel, self.test_entity_dict)

    @patch("core.repositories.generic_repositories.cache")
    @patch("core.repositories.generic_repositories.model_to_dict")
    def test_get_all_entities_no_cache(self, mock_model_to_dict, mock_cache):
        # Arrange: simulate cache miss.
        mock_cache.get.return_value = None
        DummyModel.objects.all.return_value = [self.test_entity]
        mock_model_to_dict.return_value = self.test_entity_dict

        # Act
        result = self.repo.get_all_entities(self.cache_model)

        # Assert
        self.assertEqual(result, [self.test_entity])
        expected_data = json.dumps([self.test_entity_dict])
        mock_cache.set.assert_called_once_with(self.cache_key,
                                               expected_data,
                                               timeout=300)

    # --- Tests for get_entities_with_pagination ---

    @patch("core.repositories.generic_repositories.cache")
    def test_get_entities_with_pagination_cache_hit(self, mock_cache):
        # Arrange: simulate cached paginated data.
        paginated_data = {"data": [self.test_entity_dict], "count": 1}
        mock_cache.get.return_value = json.dumps(paginated_data)

        # Act
        result = self.repo.get_entities_with_pagination(
            0, 10, self.cache_model)

        # Assert
        self.assertEqual(result, paginated_data)
        mock_cache.get.assert_called_once_with(self.cache_key)

    @patch("core.repositories.generic_repositories.cache")
    @patch("core.repositories.generic_repositories.model_to_dict")
    def test_get_entities_with_pagination_no_cache(self, mock_model_to_dict,
                                                   mock_cache):
        # Arrange: simulate cache miss.
        mock_cache.get.return_value = None

        # Use FakeQuerySet instead of a plain list.
        fake_queryset = FakeQuerySet([self.test_entity])
        DummyModel.objects.all.return_value = fake_queryset
        mock_model_to_dict.return_value = self.test_entity_dict

        # Act
        result = self.repo.get_entities_with_pagination(
            0, 10, self.cache_model)

        # Assert
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["data"], fake_queryset)
        expected_cache_data = json.dumps({
            "data": [self.test_entity_dict],
            "count": 1
        })
        mock_cache.set.assert_called_once_with(self.cache_key,
                                               expected_cache_data,
                                               timeout=300)
