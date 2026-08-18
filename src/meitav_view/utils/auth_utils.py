import logging

from fastapi import Header, HTTPException, Request

from meitav_view.model.config import Config

logger = logging.getLogger(__name__)


def is_authenticated(
    x_email: str | None = None,
    request: Request | None = None,
) -> bool:
    config = Config()
    allowed_users = config.get("allowed_users", [])
    if len(allowed_users) == 0:
        logger.debug("allowed users undefined accepts all")
        return True
    is_allowed = x_email in allowed_users
    if not is_allowed and request is not None:
        logger.warning(
            f"{x_email} is not Authorized, request {request.url} headers:{request.headers}",
        )
    return is_allowed


def require_authentication(
    request: Request,
    x_email: str | None = Header(default=None, alias="X-Email"),
) -> str | None:
    if not is_authenticated(x_email=x_email, request=request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_email
