import logging

import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import select

from ..extensions import db
from ..models import User, UserRole

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Auth-layer errors mapped to HTTP responses by the controller."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _build_tokens(user: User) -> tuple[str, str]:
    claims = {"role": user.role.value}
    access = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(user.id), additional_claims=claims)
    return access, refresh


def register_user(email: str, password: str) -> tuple[User, str, str]:
    email = _normalize_email(email)

    existing = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if existing is not None:
        raise AuthError("Email is already registered", status_code=409)

    user = User(
        email=email,
        password_hash=hash_password(password),
        role=UserRole.USER,
    )
    db.session.add(user)
    db.session.commit()

    logger.info("Registered user id=%s email=%s", user.id, user.email)

    access, refresh = _build_tokens(user)
    return user, access, refresh


def authenticate_user(email: str, password: str) -> tuple[User, str, str]:
    email = _normalize_email(email)

    user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        # Identical message in both branches to avoid leaking which half failed.
        raise AuthError("Invalid email or password", status_code=401)

    access, refresh = _build_tokens(user)
    logger.info("Authenticated user id=%s", user.id)
    return user, access, refresh
