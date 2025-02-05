import unittest
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

# Import the API views that you want to test.
from user.views import (AuthenticateUserView, CompletePasswordResetView,
                        ConfirmUserRegistrationView, GetUserByIdView,
                        InitiatePasswordResetView, RegisterUserView,
                        UpdateUserView)

# Dummy responses for tests.
DUMMY_USER_RESPONSE = {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
}
DUMMY_CONFIRM_RESPONSE = {"status": "confirmed"}
DUMMY_AUTH_RESPONSE = {"token": "fake_token"}
DUMMY_PWD_RESET_RESPONSE = {"message": "reset initiated"}
DUMMY_COMPLETE_RESET_RESPONSE = {"message": "reset completed"}


class TestUserApiViews(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.valid_registration_data = {
            "username": "testuser",
            "password": "testpass",
            "email": "test@example.com",
        }
        self.valid_confirmation_data = {
            "username": "testuser",
            "confirmationCode": "123456",
        }
        self.valid_auth_data = {
            "username": "testuser",
            "password": "testpass",
        }
        self.valid_initiate_reset_data = {"username": "testuser"}
        self.valid_complete_reset_data = {
            "username": "testuser",
            "newPassword": "newpass",
            "confirmationCode": "654321",
        }
        self.valid_update_data = {"email": "newemail@example.com"}

    # -------------------------
    # Tests for RegisterUserView
    # -------------------------
    @patch("user.views.userService")
    def test_register_user_missing_fields(self, mock_userService):
        request = self.factory.post("/api/user/register/",
                                    data={},
                                    format="json")
        view = RegisterUserView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.data
        self.assertFalse(response_data["success"])
        self.assertIn("Missing required fields", response_data["message"])
        # Ensure the save method was not called.
        mock_userService.save.assert_not_called()

    @patch("user.views.userService")
    def test_register_user_success(self, mock_userService):
        # Configure the userService.save to return a dummy user.
        mock_userService.save.return_value = DUMMY_USER_RESPONSE

        request = self.factory.post("/api/user/register/",
                                    data=self.valid_registration_data,
                                    format="json")
        view = RegisterUserView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["data"], DUMMY_USER_RESPONSE)
        self.assertEqual(response_data["message"],
                         "User registered successfully")
        mock_userService.save.assert_called_once_with(
            self.valid_registration_data)

    # -------------------------
    # Tests for ConfirmUserRegistrationView
    # -------------------------
    @patch("user.views.userService")
    def test_confirm_user_registration_missing_fields(self, mock_userService):
        request = self.factory.post("/api/user/confirm/",
                                    data={},
                                    format="json")
        view = ConfirmUserRegistrationView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        mock_userService.confirm_registration.assert_not_called()

    @patch("user.views.userService")
    def test_confirm_user_registration_success(self, mock_userService):
        mock_userService.confirm_registration.return_value = (
            DUMMY_CONFIRM_RESPONSE)

        request = self.factory.post("/api/user/confirm/",
                                    data=self.valid_confirmation_data,
                                    format="json")
        view = ConfirmUserRegistrationView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], DUMMY_CONFIRM_RESPONSE)
        self.assertEqual(response.data["message"],
                         "User confirmed successfully")
        mock_userService.confirm_registration.assert_called_once_with(
            self.valid_confirmation_data["username"],
            self.valid_confirmation_data["confirmationCode"])

    # -------------------------
    # Tests for AuthenticateUserView
    # -------------------------
    @patch("user.views.userService")
    def test_authenticate_user_missing_fields(self, mock_userService):
        request = self.factory.post("/api/user/authenticate/",
                                    data={},
                                    format="json")
        view = AuthenticateUserView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_userService.authenticate.assert_not_called()

    @patch("user.views.userService")
    def test_authenticate_user_success(self, mock_userService):
        mock_userService.authenticate.return_value = DUMMY_AUTH_RESPONSE

        request = self.factory.post("/api/user/authenticate/",
                                    data=self.valid_auth_data,
                                    format="json")
        view = AuthenticateUserView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], DUMMY_AUTH_RESPONSE)
        self.assertEqual(response.data["message"], "Authentication successful")
        mock_userService.authenticate.assert_called_once_with(
            self.valid_auth_data["username"], self.valid_auth_data["password"])

    # -------------------------
    # Tests for InitiatePasswordResetView
    # -------------------------
    @patch("user.views.userService")
    def test_initiate_password_reset_missing_username(self, mock_userService):
        request = self.factory.post("/api/user/password-reset/initiate/",
                                    data={},
                                    format="json")
        view = InitiatePasswordResetView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_userService.initiate_password_reset.assert_not_called()

    @patch("user.views.userService")
    def test_initiate_password_reset_success(self, mock_userService):
        mock_userService.initiate_password_reset.return_value = (
            DUMMY_PWD_RESET_RESPONSE)
        request = self.factory.post("/api/user/password-reset/initiate/",
                                    data=self.valid_initiate_reset_data,
                                    format="json")
        view = InitiatePasswordResetView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], DUMMY_PWD_RESET_RESPONSE)
        self.assertIn("Password reset initiated successfully",
                      response.data["message"])
        mock_userService.initiate_password_reset.assert_called_once_with(
            self.valid_initiate_reset_data["username"])

    # -------------------------
    # Tests for CompletePasswordResetView
    # -------------------------
    @patch("user.views.userService")
    def test_complete_password_reset_missing_fields(self, mock_userService):
        request = self.factory.post("/api/user/password-reset/complete/",
                                    data={},
                                    format="json")
        view = CompletePasswordResetView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_userService.complete_password_reset.assert_not_called()

    @patch("user.views.userService")
    def test_complete_password_reset_success(self, mock_userService):
        mock_userService.complete_password_reset.return_value = (
            DUMMY_COMPLETE_RESET_RESPONSE)
        request = self.factory.post("/api/user/password-reset/complete/",
                                    data=self.valid_complete_reset_data,
                                    format="json")
        view = CompletePasswordResetView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], DUMMY_COMPLETE_RESET_RESPONSE)
        self.assertEqual(response.data["message"],
                         "Password reset completed successfully")
        mock_userService.complete_password_reset.assert_called_once_with(
            self.valid_complete_reset_data["username"],
            self.valid_complete_reset_data["newPassword"],
            self.valid_complete_reset_data["confirmationCode"],
        )

    # -------------------------
    # Tests for GetUserByIdView
    # -------------------------
    @patch("user.views.userService")
    def test_get_user_by_id_missing_id(self, mock_userService):
        # Simulate missing id by passing None.
        request = self.factory.get("/api/user/0/")
        view = GetUserByIdView.as_view()
        response = view(request, id=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_userService.findById.assert_not_called()

    @patch("user.views.userService")
    def test_get_user_by_id_not_found(self, mock_userService):
        mock_userService.findById.return_value = None
        request = self.factory.get("/api/user/999/")
        view = GetUserByIdView.as_view()
        response = view(request, id=999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_userService.findById.assert_called_once_with(999)

    @patch("user.views.userService")
    def test_get_user_by_id_success(self, mock_userService):
        mock_userService.findById.return_value = DUMMY_USER_RESPONSE
        request = self.factory.get("/api/user/1/")
        view = GetUserByIdView.as_view()
        response = view(request, id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], DUMMY_USER_RESPONSE)
        mock_userService.findById.assert_called_once_with(1)

    # -------------------------
    # Tests for UpdateUserView
    # -------------------------
    @patch("user.views.userService")
    def test_update_user_missing_data(self, mock_userService):
        request = self.factory.put("/api/user/1/update/",
                                   data={},
                                   format="json")
        view = UpdateUserView.as_view()
        response = view(request, id=1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_userService.update.assert_not_called()

    @patch("user.views.userService")
    def test_update_user_not_found(self, mock_userService):
        mock_userService.update.return_value = None
        request = self.factory.put("/api/user/1/update/",
                                   data=self.valid_update_data,
                                   format="json")
        view = UpdateUserView.as_view()
        response = view(request, id=1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_userService.update.assert_called_once_with(
            1, self.valid_update_data)

    @patch("user.views.userService")
    def test_update_user_success(self, mock_userService):
        updated_user = {
            "id": 1,
            "username": "testuser",
            "email": "newemail@example.com"
        }
        mock_userService.update.return_value = updated_user
        request = self.factory.put("/api/user/1/update/",
                                   data=self.valid_update_data,
                                   format="json")
        view = UpdateUserView.as_view()
        response = view(request, id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], updated_user)
        self.assertEqual(response.data["message"], "User updated successfully")
        mock_userService.update.assert_called_once_with(
            1, self.valid_update_data)


if __name__ == '__main__':
    unittest.main()
