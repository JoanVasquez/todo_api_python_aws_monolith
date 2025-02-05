import json
from typing import Any, Dict, Optional

from django.core.cache import cache
from django.forms.models import model_to_dict

from core.models import User
from core.repositories.user_repository import UserRepository
from core.services.authentication_service import AuthenticationService
from core.services.generic_service import GenericService
from core.services.password_service import PasswordService
from core.utils.cache_util_model import CacheModel
from core.utils.logger import get_logger
from core.utils.reset_password_input_validator import \
    reset_password_input_validator

logger = get_logger(__name__)


class UserService(GenericService[User]):
    user_repository: UserRepository = UserRepository()

    def __init__(self) -> None:
        super().__init__(UserService.user_repository)
        self.auth_service = AuthenticationService()
        self.password_service = PasswordService()

    def save(self,
             entity: User,
             cache_model: Optional[CacheModel] = None) -> Optional[User]:
        try:
            logger.info(f"[UserService] Registering user: {entity.username}")
            self.auth_service.register_user(entity.username, entity.password,
                                            entity.email)
            encrypted_password = self.password_service.get_password_encrypted(
                entity.password)
            logger.info("[UserService] Password encrypted.")
            user = UserService.user_repository.create_entity(
                User(
                    username=entity.username,
                    password=encrypted_password,
                    email=entity.email,
                ),
                cache_model,
            )
            logger.info(
                f"[UserService] User created in database: {entity.username}")
            return user
        except Exception as error:
            logger.error(
                f"[UserService] Registration failed for user: "
                f"{entity.username}",
                exc_info=True,
            )
            raise Exception("Registration failed") from error

    def confirm_registration(self, username: str,
                             confirmation_code: str) -> Dict[str, Any]:
        try:
            logger.info(
                f"[UserService] Confirming registration for user: {username}")
            response = self.auth_service.confirm_user_registration(
                username, confirmation_code)
            logger.info(
                f"[UserService] User confirmed successfully: {username}")
            return response
        except Exception as error:
            logger.error(
                f"[UserService] Confirmation failed for user: {username}",
                exc_info=True,
            )
            raise Exception("User confirmation failed") from error

    def authenticate(self, username: str, password: str) -> Dict[str, str]:
        try:
            logger.info(
                f"[UserService] Starting authentication for user: {username}")
            token = self.auth_service.authenticate_user(username, password)
            cached_user = cache.get(f"user:{username}")
            if cached_user:
                user = json.loads(cached_user)
            else:
                user = UserService.user_repository.find_user_by_username(
                    username)
            if not user:
                logger.warning(
                    f"[UserService] User not found in cache or database: "
                    f"{username}")
                raise Exception("User not found")
            if not cached_user:
                cache.set(
                    f"user:{username}",
                    json.dumps(model_to_dict(user)),
                    3600,
                )
            logger.info(
                f"[UserService] User authenticated successfully: {username}")
            return {"token": token}
        except Exception as error:
            logger.error(
                f"[UserService] Authentication process failed for user: "
                f"{username}",
                exc_info=True,
            )
            raise Exception(
                "Authentication failed: Invalid username or password"
            ) from error

    def initiate_password_reset(self, username: str) -> Dict[str, Any]:
        try:
            logger.info(
                f"[UserService] Initiating password reset for user: {username}"
            )
            response = self.password_service.initiate_user_password_reset(
                username)
            logger.info(
                f"[UserService] Password reset initiated successfully for "
                f"user: {username}")
            return {
                "message":
                ("Password reset initiated. Check your email for the code."),
                "response":
                response,
            }
        except Exception as error:
            logger.error(
                f"[UserService] Failed to initiate password reset for user: "
                f"{username}",
                exc_info=True,
            )
            raise Exception("Failed to initiate password reset") from error

    def complete_password_reset(self, username: str, new_password: str,
                                confirmation_code: str) -> Dict[str, Any]:
        try:
            logger.info(
                f"[UserService] Starting password reset for user: {username}")
            reset_password_input_validator(username, new_password,
                                           confirmation_code)
            response = self.password_service.complete_user_password_reset(
                username, new_password, confirmation_code)
            logger.info(
                f"[UserService] Cognito password reset completed for user: "
                f"{username}")
            encrypted_password = self.password_service.get_password_encrypted(
                new_password)
            logger.info(
                f"[UserService] Password encrypted successfully for user: "
                f"{username}")
            user = UserService.user_repository.find_user_by_username(username)
            if not user:
                logger.warning(
                    f"[UserService] User not found in repository: {username}")
                raise Exception("User not found in the repository")
            UserService.user_repository.update_entity(
                user.id, {"password": encrypted_password})
            logger.info(
                f"[UserService] Password updated in the database for user: "
                f"{username}")
            logger.info(
                f"[UserService] Password reset successfully completed for "
                f"user: {username}")
            return {
                "message": "Password reset successfully completed.",
                "response": response,
            }
        except Exception as error:
            logger.error(
                f"[UserService] Failed to complete password reset for user: "
                f"{username}",
                exc_info=True,
            )
            raise Exception("Failed to complete password reset") from error
