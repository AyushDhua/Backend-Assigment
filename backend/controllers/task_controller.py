from flask import request
from marshmallow import ValidationError

from ..middlewares import get_current_user
from ..schemas.task_schema import (
    TaskCreateSchema,
    TaskOutputSchema,
    TaskUpdateSchema,
)
from ..services import task_service
from ..services.task_service import TaskError
from ..utils.response import error_response, success_response

_create_schema = TaskCreateSchema()
_update_schema = TaskUpdateSchema()
_output_schema = TaskOutputSchema()
_output_many_schema = TaskOutputSchema(many=True)


def list_tasks_view():
    user = get_current_user()
    status_q = request.args.get("status")

    try:
        tasks = task_service.list_tasks(user, status_filter=status_q)
    except TaskError as err:
        return error_response(err.message, err.status_code)

    return success_response(
        data=_output_many_schema.dump(tasks),
        message="Tasks fetched",
    )


def create_task_view():
    user = get_current_user()
    try:
        payload = _create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Validation failed", 400, details=err.messages)

    task = task_service.create_task(
        user,
        title=payload["title"],
        description=payload.get("description"),
        status=payload["status"],
    )
    return success_response(
        data=_output_schema.dump(task),
        message="Task created",
        status_code=201,
    )


def update_task_view(task_id: int):
    user = get_current_user()
    try:
        payload = _update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Validation failed", 400, details=err.messages)

    if not payload:
        return error_response(
            "Validation failed",
            400,
            message="At least one updatable field must be provided",
        )

    try:
        task = task_service.update_task(task_id, user, payload)
    except TaskError as err:
        return error_response(err.message, err.status_code)

    return success_response(
        data=_output_schema.dump(task),
        message="Task updated",
    )


def delete_task_view(task_id: int):
    user = get_current_user()
    try:
        task_service.delete_task(task_id, user)
    except TaskError as err:
        return error_response(err.message, err.status_code)
    return success_response(message="Task deleted")
