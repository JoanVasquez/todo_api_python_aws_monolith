import json
import unittest
from unittest.mock import MagicMock, patch

from core.models import User
# Import the class under test and its dependencies.
from core.repositories.user_repository import UserRepository
from core.utils.cache_util_model import CacheModel

# --- Dummy User for testing ---


class DummyUser:

    def __init__(self, username):
        self.username = username


# Create a dummy user instance and its dictionary representation.
dummy_user = DummyUser("testuser")
dummy_user_dict = {"username": "testuser"}

# --- Unit Tests ---


class TestUserRepository(unittest.TestCase):

    def setUp(self) -> None:
        # Ensure the User model's manager is a MagicMock
        # so that we can control queries.
        User.objects = MagicMock()
        self.repo = UserRepository()
        self.cache_model = CacheModel(key="user_test_key", expiration=300)

    @patch("core.repositories.user_repository.cache")
    @patch("core.repositories.user_repository.deserialize_instance")
    def test_find_user_by_username_cache_hit(self, mock_deserialize,
                                             mock_cache):
        """
        Test that if the cache returns a value, the repository uses the cached
        data.
        """
        # Arrange: simulate a cache hit by returning a JSON string
        # representing the user.
        mock_cache.get.return_value = json.dumps(dummy_user_dict)
        mock_deserialize.return_value = dummy_user

        # Act
        result = self.repo.find_user_by_username("testuser", self.cache_model)

        # Assert
        self.assertEqual(result, dummy_user)
        mock_cache.get.assert_called_once_with(self.cache_model.key)
        mock_deserialize.assert_called_once_with(User, dummy_user_dict)

    @patch("core.repositories.user_repository.cache")
    @patch("core.repositories.user_repository.model_to_dict")
    def test_find_user_by_username_no_cache_found(self, mock_model_to_dict,
                                                  mock_cache):
        """
        Test that if the cache returns nothing, the repository queries the DB,
        caches the result, and returns the user.
        """
        # Arrange: simulate a cache miss.
        mock_cache.get.return_value = None
        # Simulate that the database query returns a user.
        User.objects.filter.return_value.first.return_value = dummy_user
        mock_model_to_dict.return_value = dummy_user_dict

        # Act
        result = self.repo.find_user_by_username("testuser", self.cache_model)

        # Assert
        self.assertEqual(result, dummy_user)
        User.objects.filter.assert_called_once_with(username="testuser")
        expected_data = json.dumps(dummy_user_dict)
        mock_cache.set.assert_called_once_with(
            self.cache_model.key,
            expected_data,
            timeout=self.cache_model.expiration,
        )

    @patch("core.repositories.user_repository.cache")
    def test_find_user_by_username_not_found(self, mock_cache):
        """
        Test that if the user is not found in the DB, the method returns None.
        (It logs a warning and raises an exception internally that is caught.)
        """
        # Arrange: simulate a cache miss and no matching user in the DB.
        mock_cache.get.return_value = None
        User.objects.filter.return_value.first.return_value = None

        # Act
        result = self.repo.find_user_by_username("nonexistent",
                                                 self.cache_model)

        # Assert
        self.assertIsNone(result)
        User.objects.filter.assert_called_once_with(username="nonexistent")

    @patch("core.repositories.user_repository.cache")
    def test_find_user_by_username_exception(self, mock_cache):
        """
        Test that if an exception occurs (for example during the DB query),
        the method catches it, logs the error, and returns None.
        """
        # Arrange: simulate a cache miss and then force an exception on the
        # DB query.
        mock_cache.get.return_value = None
        User.objects.filter.side_effect = Exception("DB error")

        # Act
        result = self.repo.find_user_by_username("testuser", self.cache_model)

        # Assert
        self.assertIsNone(result)
