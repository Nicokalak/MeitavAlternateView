import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import request

from meitav_view.model.config import Config

email_header = "X-Email"
logger = logging.getLogger(__name__)


def require_authentication(func: Callable[..., Any]) -> Any:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Implement your authentication logic here
        authenticated = is_authenticated()

        if not authenticated:
            # Return a 401 Unauthorized response with a JSON message
            return {"error": "Unauthorized"}, 401

        # Call the original function if authentication is successful
        return func(*args, **kwargs)

    return wrapper


def is_authenticated() -> bool:
    config = Config()
    allowed_users = config.get("allowed_users", [])
    if len(allowed_users) == 0:
        logger.debug("allowed users undefined accepts all")
        return True
    user = request.headers.get(email_header)
    is_allowed = user in allowed_users
    if not is_allowed:
        logger.warning(
            f"{user} is not Authorized, request {request.url} headers:{request.headers}",
        )
    return is_allowed
