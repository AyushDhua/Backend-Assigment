import logging
from functools import wraps

from flask import g
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import select

from ..extensions import db
from ..models import User
from ..utils.response import error_response

logger = logging.getLogger(__name__)


def auth_required(fn):
    """Verify the JWT and attach the User to ``flask.g.current_user``.

    Token-shape failures (missing / malformed / expired) are handled by the
    Flask-JWT-Extended loaders registered in ``app.py``. This wrapper covers
    the post-verification step: resolving the ``sub`` claim into a database
    user. If the user no longer exists, the request is rejected with 401.
    """

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        try:
            user_id = int(identity)
        except (TypeError, ValueError):
            logger.warning("JWT identity is not an integer: %r", identity)
            return error_response("Invalid token", 401, message="Malformed subject claim")

        user = db.session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if user is None:
            logger.warning("JWT references missing user id=%s", user_id)
            return error_response("Unauthorized", 401, message="User no longer exists")

        g.current_user = user
        g.jwt_claims = get_jwt()
        return fn(*args, **kwargs)

    return wrapper


def get_current_user() -> User:
    """Return the User attached by ``auth_required``.

    Raises if called outside an authenticated request — an actual programming
    error, not a runtime auth failure.
    """
    user = getattr(g, "current_user", None)
    if user is None:
        raise RuntimeError(
            "get_current_user() called without an active auth_required scope"
        )
    return user


def get_current_claims() -> dict:
    return getattr(g, "jwt_claims", {}) or {}
