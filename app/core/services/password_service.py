from core.utils.cognito_util import (complete_password_reset,
                                     initiate_password_reset)
from core.utils.kms_util import encrypt_password
from core.utils.logger import get_logger
from core.utils.ssm_util import get_cached_parameter

logger = get_logger(__name__)


class PasswordService:

    def get_password_encrypted(self, new_password: str) -> str:
        """
        Encrypt the given password using KMS and return the encrypted string.
        """
        try:
            kms_key_id = get_cached_parameter("/myapp/kms-key-id")
            return encrypt_password(new_password, kms_key_id)
        except Exception as error:
            msg = "[PasswordService] Failed to encrypt password: " f"{error}"
            logger.error(msg, exc_info=True)
            raise Exception("Failed to encrypt password") from error

    def initiate_user_password_reset(self, username: str) -> None:
        """
        Initiate a password reset for the given username using Cognito.
        """
        try:
            logger.info(("[PasswordService] Initiate user password reset in "
                         f"Cognito: {username}"))
            initiate_password_reset(username)
            logger.info(
                ("[PasswordService] Password reset initiated for user: "
                 f"{username}"))
        except Exception as error:
            msg = ("[PasswordService] Failed to initiate "
                   f"password reset for user: {username}")
            logger.error(msg, exc_info=True)
            raise Exception("Failed to initiate password reset") from error

    def complete_user_password_reset(self, username: str,
                                     confirmation_code: str,
                                     new_password: str) -> None:
        """
        Complete the password reset for the given user.
        """
        try:
            logger.info(
                ("[AuthenticationService] Completing password reset for "
                 f"user: {username}"))
            complete_password_reset(username, confirmation_code, new_password)
            logger.info(("[AuthenticationService] Password reset "
                         f"completed for user: {username}"))
        except Exception as error:
            msg = ("[AuthenticationService] Failed to complete "
                   f"password reset for user: {username}")
            logger.error(msg, exc_info=True)
            raise Exception("Failed to complete password reset") from error
