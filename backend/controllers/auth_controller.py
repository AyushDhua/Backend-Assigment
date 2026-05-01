from flask import request
from marshmallow import ValidationError

from ..schemas.auth_schema import LoginSchema, RegisterSchema, UserPublicSchema
from ..services import auth_service
from ..services.auth_service import AuthError
from ..utils.response import error_response, success_response

_register_schema = RegisterSchema()
_login_schema = LoginSchema()
_user_schema = UserPublicSchema()


def register():
    try:
        payload = _register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Validation failed", 400, details=err.messages)

    try:
        user, access, refresh = auth_service.register_user(
            email=payload["email"],
            password=payload["password"],
        )
    except AuthError as err:
        return error_response(err.message, err.status_code)

    return success_response(
        data={
            "user": _user_schema.dump(user),
            "access_token": access,
            "refresh_token": refresh,
        },
        message="User registered successfully",
        status_code=201,
    )


def login():
    try:
        payload = _login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Validation failed", 400, details=err.messages)

    try:
        user, access, refresh = auth_service.authenticate_user(
            email=payload["email"],
            password=payload["password"],
        )
    except AuthError as err:
        return error_response(err.message, err.status_code)

    return success_response(
        data={
            "user": _user_schema.dump(user),
            "access_token": access,
            "refresh_token": refresh,
        },
        message="Login successful",
    )
