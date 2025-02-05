import os
import unittest
from unittest.mock import patch

# It’s assumed that your code is in a module named cognito_service.py.
import core.utils.cognito_util as cognito_service


class TestCognitoService(unittest.TestCase):

    def setUp(self):
        # Set the required environment variables
        os.environ["COGNITO_CLIENT_ID_SSM_PATH"] = "fake/path"
        os.environ["AWS_REGION"] = "us-east-1"
        # A mapping for fake SSM parameter values.
        # Note: the code calls get_cached_parameter twice on the client-id SSM
        # path, so we return an intermediate value then the final client-id.
        self.fake_ssm_params = {
            "fake/path": "fake-client-id-ssm",
            "fake-client-id-ssm": "fake-client-id",
            "/myapp/cognito/user-pool-id": "fake-user-pool-id",
        }

    def fake_get_cached_parameter(self, param):
        """
        A fake get_cached_parameter implementation that simply returns a value
        from the fake_ssm_params dict or returns the param if not found.
        """
        return self.fake_ssm_params.get(param, param)

    @patch("core.utils.cognito_util.cognito_client")
    @patch("core.utils.cognito_util.get_cached_parameter")
    def test_authenticate_success(self, mock_get_cached_parameter,
                                  mock_cognito_client):
        # Set our fake SSM parameter retrieval behavior.
        mock_get_cached_parameter.side_effect = self.fake_get_cached_parameter

        # Prepare a fake response from admin_initiate_auth
        fake_response = {"AuthenticationResult": {"IdToken": "fake-id-token"}}
        mock_cognito_client.admin_initiate_auth.return_value = fake_response

        # Call the function under test.
        token = cognito_service.authenticate("testuser", "testpassword")

        # Assert that the returned token is what we expect.
        self.assertEqual(token, "fake-id-token")

        # Verify that admin_initiate_auth was called with the expected
        # arguments.
        mock_cognito_client.admin_initiate_auth.assert_called_with(
            UserPoolId="fake-user-pool-id",
            ClientId="fake-client-id",
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                "USERNAME": "testuser",
                "PASSWORD": "testpassword"
            },
        )

    @patch("core.utils.cognito_util.cognito_client")
    @patch("core.utils.cognito_util.get_cached_parameter")
    def test_register_user_success(self, mock_get_cached_parameter,
                                   mock_cognito_client):
        mock_get_cached_parameter.side_effect = self.fake_get_cached_parameter

        # Call the register_user function.
        result = cognito_service.register_user("newuser", "newpassword",
                                               "newuser@example.com")

        # Assert that the response is as expected.
        self.assertEqual(result, {"message": "User registered successfully"})

        # Verify that sign_up was called with the expected parameters.
        mock_cognito_client.sign_up.assert_called_with(
            ClientId="fake-client-id",
            Username="newuser",
            Password="newpassword",
            UserAttributes=[{
                "Name": "email",
                "Value": "newuser@example.com"
            }],
        )

    @patch("core.utils.cognito_util.cognito_client")
    @patch("core.utils.cognito_util.get_cached_parameter")
    def test_confirm_user_registration_success(self, mock_get_cached_parameter,
                                               mock_cognito_client):
        mock_get_cached_parameter.side_effect = self.fake_get_cached_parameter

        # Call the confirm_user_registration function.
        result = cognito_service.confirm_user_registration(
            "confirmuser", "123456")

        # Assert the expected response.
        self.assertEqual(result, {"message": "User confirmed successfully"})

        # Verify that confirm_sign_up was called with the correct parameters.
        mock_cognito_client.confirm_sign_up.assert_called_with(
            ClientId="fake-client-id",
            Username="confirmuser",
            ConfirmationCode="123456",
        )

    @patch("core.utils.cognito_util.cognito_client")
    @patch("core.utils.cognito_util.get_cached_parameter")
    def test_initiate_password_reset_success(self, mock_get_cached_parameter,
                                             mock_cognito_client):
        mock_get_cached_parameter.side_effect = self.fake_get_cached_parameter

        # Call the initiate_password_reset function.
        result = cognito_service.initiate_password_reset("resetuser")

        # Assert that the expected response is returned.
        self.assertEqual(
            result,
            {
                "message":
                "Password reset initiated. "
                "Check your email for the code."
            },
        )

        # Verify that forgot_password was called with the correct parameters.
        mock_cognito_client.forgot_password.assert_called_with(
            ClientId="fake-client-id", Username="resetuser")

    @patch("core.utils.cognito_util.cognito_client")
    @patch("core.utils.cognito_util.get_cached_parameter")
    def test_complete_password_reset_success(self, mock_get_cached_parameter,
                                             mock_cognito_client):
        mock_get_cached_parameter.side_effect = self.fake_get_cached_parameter

        # Call the complete_password_reset function.
        result = cognito_service.complete_password_reset(
            "resetuser", "newpassword", "654321")

        # Assert that the expected response is returned.
        self.assertEqual(result, {"message": "Password reset successfully"})

        # Verify that confirm_forgot_password was called with the correct
        # parameters.
        mock_cognito_client.confirm_forgot_password.assert_called_with(
            ClientId="fake-client-id",
            Username="resetuser",
            Password="newpassword",
            ConfirmationCode="654321",
        )

    @patch("core.utils.cognito_util.get_cached_parameter")
    def test_missing_env_var(self, mock_get_cached_parameter):
        # Remove the required environment variable.
        if "COGNITO_CLIENT_ID_SSM_PATH" in os.environ:
            del os.environ["COGNITO_CLIENT_ID_SSM_PATH"]

        # When the environment variable is missing, the function will catch
        # the ValueError and raise a generic Exception with the message
        # "Authentication failed".
        with self.assertRaises(Exception) as context:
            cognito_service.authenticate("user", "password")
        self.assertIn("Authentication failed", str(context.exception))
