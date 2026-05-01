import logging
from functools import wraps
from typing import Iterable, Union

from flask import g

from ..models import UserRole
from ..utils.response import error_response

logger = logging.getLogger(__name__)

RoleLike = Union[UserRole, str]


def _normalize(role: RoleLike) -> str:
    if isinstance(role, UserRole):
        return role.value
    return str(role).strip().upper()


def roles_required(*allowed: RoleLike):
    """Gate a view by role. Must be applied AFTER ``auth_required``.

    Usage::

        @auth_required
        @roles_required(UserRole.ADMIN)
        def admin_only(): ...

        @auth_required
        @roles_required(UserRole.USER, UserRole.ADMIN)
        def either(): ...
    """
    if not allowed:
        raise ValueError("roles_required(...) needs at least one role")

    allowed_values = {_normalize(r) for r in allowed}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if user is None:
                logger.error(
                    "roles_required ran without auth_required on %s", fn.__qualname__
                )
                return error_response(
                    "Unauthorized",
                    401,
                    message="Authentication required",
                )

            if user.role.value not in allowed_values:
                logger.info(
                    "Role %s denied access to %s (allowed=%s)",
                    user.role.value,
                    fn.__qualname__,
                    sorted(allowed_values),
                )
                return error_response(
                    "Forbidden",
                    403,
                    message="You do not have permission to access this resource",
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(fn):
    """Shortcut for ``roles_required(UserRole.ADMIN)``."""
    return roles_required(UserRole.ADMIN)(fn)


def is_admin(user=None) -> bool:
    user = user if user is not None else getattr(g, "current_user", None)
    return user is not None and user.role == UserRole.ADMIN


def is_owner_or_admin(resource_owner_id: int, user=None) -> bool:
    """Authorization predicate for the "USER → own data, ADMIN → all data" rule.

    Use in controllers/services to gate per-resource access::

        if not is_owner_or_admin(task.user_id):
            return error_response("Forbidden", 403)
    """
    user = user if user is not None else getattr(g, "current_user", None)
    if user is None:
        return False
    return user.role == UserRole.ADMIN or user.id == resource_owner_id


def filter_for_current_user(query, owner_column, user=None):
    """Apply the ownership rule to a SQLAlchemy ``select(...)`` query.

    ADMINs see everything; USERs are restricted to rows they own. Returns the
    (possibly modified) query so it composes naturally::

        stmt = select(Task)
        stmt = filter_for_current_user(stmt, Task.user_id)
    """
    user = user if user is not None else getattr(g, "current_user", None)
    if user is None or user.role == UserRole.ADMIN:
        return query
    return query.where(owner_column == user.id)
