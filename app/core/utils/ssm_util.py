import os

import boto3
from botocore.exceptions import ClientError

from core.utils.logger import get_logger

logger = get_logger(__name__)


def get_cached_parameter(name: str) -> str:
    """
    Fetch a parameter value from AWS SSM. In local/test environments,
    simply return the value from an environment variable.
    """
    env = os.environ.get("DJANGO_ENV", "").lower()
    if env in ["local", "test"]:
        # In local or testing, use the value directly from the environment.
        value = os.environ.get(name)
        if value is None:
            raise Exception(f"Environment variable '{name}' is not set")
        logger.info(f"[get_cached_parameter] Using environment variable "
                    f"'{name}': {value}")
        return value

    # Production: fetch the parameter from SSM.
    ssm_client = boto3.client("ssm")
    try:
        logger.info(
            f"[get_cached_parameter] Fetching parameter '{name}' from SSM.")
        response = ssm_client.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]
    except ClientError as error:
        logger.error(
            f"[get_cached_parameter] Error fetching parameter "
            f"'{name}': {error}",
            exc_info=True,
        )
        raise Exception(f"Could not fetch parameter: {name}") from error
