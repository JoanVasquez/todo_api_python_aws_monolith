import unittest
from unittest.mock import patch

# Import the PasswordService class.
from core.services.password_service import PasswordService


class TestPasswordService(unittest.TestCase):

    def setUp(self):
        self.service = PasswordService()
        self.username = "testuser"
        self.new_password = "newpass"
        self.confirmation_code = "123456"
        self.kms_key_id = "kms-key-123"
        self.encrypted_password = "encrypted-newpass"

    # --- Tests for get_password_encrypted ---

    @patch('core.services.password_service.encrypt_password')
    @patch('core.services.password_service.get_cached_parameter')
    @patch('core.services.password_service.logger')
    def test_get_password_encrypted_success(self, mock_logger, mock_get_param,
                                            mock_encrypt):
        """
        Test that get_password_encrypted returns the encrypted string when KMS
        encryption succeeds.
        """
        # Set up the mocks:
        mock_get_param.return_value = self.kms_key_id
        mock_encrypt.return_value = self.encrypted_password

        # Call the method under test.
        result = self.service.get_password_encrypted(self.new_password)

        # Verify the correct functions were called with the expected
        # parameters.
        mock_get_param.assert_called_once_with("/myapp/kms-key-id")
        mock_encrypt.assert_called_once_with(self.new_password,
                                             self.kms_key_id)
        self.assertEqual(result, self.encrypted_password)

    @patch('core.services.password_service.encrypt_password')
    @patch('core.services.password_service.get_cached_parameter')
    @patch('core.services.password_service.logger')
    def test_get_password_encrypted_failure(self, mock_logger, mock_get_param,
                                            mock_encrypt):
        """
        Test that get_password_encrypted raises an exception if an error occurs
        (e.g. parameter not found).
        """
        # Simulate an exception when getting the KMS key.
        mock_get_param.side_effect = Exception("Parameter not found")

        with self.assertRaises(Exception) as context:
            self.service.get_password_encrypted(self.new_password)
        self.assertIn("Failed to encrypt password", str(context.exception))
        mock_logger.error.assert_called()  # Ensure that the error was logged.

    # --- Tests for initiate_user_password_reset ---

    @patch('core.services.password_service.initiate_password_reset')
    @patch('core.services.password_service.logger')
    def test_initiate_user_password_reset_success(self, mock_logger,
                                                  mock_initiate):
        """
        Test that initiate_user_password_reset calls initiate_password_reset
        correctly.
        """
        # Call the method.
        self.service.initiate_user_password_reset(self.username)
        # Verify that initiate_password_reset was called with the correct
        # username.
        mock_initiate.assert_called_once_with(self.username)
        self.assertTrue(mock_logger.info.called)

    @patch('core.services.password_service.initiate_password_reset')
    @patch('core.services.password_service.logger')
    def test_initiate_user_password_reset_failure(self, mock_logger,
                                                  mock_initiate):
        """
        Test that initiate_user_password_reset raises an exception if the
        underlying call fails.
        """
        mock_initiate.side_effect = Exception("Reset error")
        with self.assertRaises(Exception) as context:
            self.service.initiate_user_password_reset(self.username)
        self.assertIn("Failed to initiate password reset",
                      str(context.exception))
        mock_logger.error.assert_called()

    # --- Tests for complete_user_password_reset ---

    @patch('core.services.password_service.complete_password_reset')
    @patch('core.services.password_service.logger')
    def test_complete_user_password_reset_success(self, mock_logger,
                                                  mock_complete):
        """
        Test that complete_user_password_reset calls complete_password_reset
        correctly.
        """
        self.service.complete_user_password_reset(self.username,
                                                  self.confirmation_code,
                                                  self.new_password)
        mock_complete.assert_called_once_with(self.username,
                                              self.confirmation_code,
                                              self.new_password)
        self.assertTrue(mock_logger.info.called)

    @patch('core.services.password_service.complete_password_reset')
    @patch('core.services.password_service.logger')
    def test_complete_user_password_reset_failure(self, mock_logger,
                                                  mock_complete):
        """
        Test that complete_user_password_reset raises an exception if the
        underlying call fails.
        """
        mock_complete.side_effect = Exception("Complete error")
        with self.assertRaises(Exception) as context:
            self.service.complete_user_password_reset(self.username,
                                                      self.confirmation_code,
                                                      self.new_password)
        self.assertIn("Failed to complete password reset",
                      str(context.exception))
        mock_logger.error.assert_called()
