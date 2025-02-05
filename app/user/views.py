from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services.user_service import UserService
from core.utils.http_response import HttpResponse
from core.utils.logger import get_logger

logger = get_logger(__name__)

userService = UserService()


class RegisterUserView(APIView):

    def post(self, request, format=None):
        try:
            # DRF automatically parses JSON request bodies into request.data
            username = request.data.get("username")
            password = request.data.get("password")
            email = request.data.get("email")

            if not username or not password or not email:
                logger.warning(
                    "[UserController] Missing user registration data")
                return Response(
                    HttpResponse.error(("Missing required fields: "
                                        "username, password, or email"), 400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = userService.save({
                "username": username,
                "password": password,
                "email": email,
            })
            return Response(
                HttpResponse.success(response, "User registered successfully"),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            logger.error("[UserController] Registration failed", exc_info=True)
            return Response(
                HttpResponse.error("Failed to register user", 500, str(error)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConfirmUserRegistrationView(APIView):

    def post(self, request, format=None):
        try:
            username = request.data.get("username")
            confirmationCode = request.data.get("confirmationCode")

            if not username or not confirmationCode:
                logger.warning("[UserController] Missing confirmation data")
                return Response(
                    HttpResponse.error(("Missing required fields: "
                                        "username or confirmationCode"), 400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = userService.confirm_registration(
                username, confirmationCode)
            return Response(
                HttpResponse.success(response, "User confirmed successfully"),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            logger.error("[UserController] User confirmation failed",
                         exc_info=True)
            return Response(
                HttpResponse.error("Failed to confirm user", 500, str(error)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AuthenticateUserView(APIView):

    def post(self, request, format=None):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username or not password:
                logger.warning("[UserController] Missing authentication data")
                return Response(
                    HttpResponse.error(
                        "Missing required fields: username or password", 400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = userService.authenticate(username, password)
            return Response(
                HttpResponse.success(response, "Authentication successful"),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            logger.error("[UserController] Authentication failed",
                         exc_info=True)
            return Response(
                HttpResponse.error("Authentication failed", 500, str(error)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InitiatePasswordResetView(APIView):

    def post(self, request, format=None):
        try:
            username = request.data.get("username")
            if not username:
                logger.warning(
                    "[UserController] Missing username for password reset")
                return Response(
                    HttpResponse.error("Username is required", 400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = userService.initiate_password_reset(username)
            return Response(
                HttpResponse.success(response,
                                     "Password reset initiated successfully"),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            logger.error("[UserController] Password reset initiation failed",
                         exc_info=True)
            return Response(
                HttpResponse.error("Failed to initiate password reset", 500,
                                   str(error)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CompletePasswordResetView(APIView):

    def post(self, request, format=None):
        try:
            username = request.data.get("username")
            newPassword = request.data.get("newPassword")
            confirmationCode = request.data.get("confirmationCode")

            if not username or not newPassword or not confirmationCode:
                logger.warning(
                    ("[UserController] Missing data for password reset "
                     "completion"))
                return Response(
                    HttpResponse.error(("Missing required fields: username, "
                                        "newPassword, or confirmationCode"),
                                       400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = userService.complete_password_reset(
                username, newPassword, confirmationCode)
            return Response(
                HttpResponse.success(response,
                                     "Password reset completed successfully"),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            logger.error("[UserController] Password reset completion failed",
                         exc_info=True)
            return Response(
                HttpResponse.error("Failed to complete password reset", 500,
                                   str(error)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetUserByIdView(APIView):

    def get(self, request, id, format=None):
        try:
            if not id:
                logger.warning(
                    "[UserController] Missing user ID in path parameters")
                return Response(
                    HttpResponse.error("User ID is required", 400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = userService.findById(int(id))
            if not user:
                logger.warning(
                    f"[UserController] User not found with ID: {id}")
                return Response(
                    HttpResponse.error("User not found", 404),
                    status=status.HTTP_404_NOT_FOUND,
                )

            logger.info(
                f"[UserController] User retrieved successfully with ID: {id}")
            return Response(
                HttpResponse.success(user, "User retrieved successfully"),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            logger.error("[UserController] Failed to fetch user by ID",
                         exc_info=True)
            return Response(
                HttpResponse.error("Failed to fetch user", 500, str(error)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateUserView(APIView):

    def put(self, request, id, format=None):
        try:
            if not id:
                logger.warning(
                    "[UserController] Missing user ID in path parameters")
                return Response(
                    HttpResponse.error("User ID is required", 400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated_data = request.data
            if not updated_data:
                logger.warning("[UserController] Missing update data")
                return Response(
                    HttpResponse.error("Update data is required", 400),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated_user = userService.update(int(id), updated_data)
            if not updated_user:
                logger.warning(
                    f"[UserController] Failed to update user with ID: {id}")
                return Response(
                    HttpResponse.error("User not found", 404),
                    status=status.HTTP_404_NOT_FOUND,
                )

            logger.info(
                f"[UserController] User updated successfully with ID: {id}")
            return Response(
                HttpResponse.success(updated_user,
                                     "User updated successfully"),
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            logger.error("[UserController] Failed to update user",
                         exc_info=True)
            return Response(
                HttpResponse.error("Failed to update user", 500, str(error)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
