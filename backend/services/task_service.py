import logging
from typing import Any

from sqlalchemy import select

from ..extensions import db
from ..middlewares import filter_for_current_user, is_owner_or_admin
from ..models import Task, TaskStatus, User

logger = logging.getLogger(__name__)


class TaskError(Exception):
    """Service-layer error mapped to an HTTP response by the controller."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def list_tasks(user: User, status_filter: str | None = None) -> list[Task]:
    stmt = select(Task).order_by(Task.created_at.desc())
    stmt = filter_for_current_user(stmt, Task.user_id, user=user)

    if status_filter is not None:
        try:
            stmt = stmt.where(Task.status == TaskStatus(status_filter))
        except ValueError:
            raise TaskError(
                f"Unknown status '{status_filter}'", status_code=400
            )

    return list(db.session.execute(stmt).scalars().all())


def get_task(task_id: int, user: User) -> Task:
    task = db.session.get(Task, task_id)
    if task is None:
        raise TaskError("Task not found", status_code=404)

    if not is_owner_or_admin(task.user_id, user=user):
        # Same code/shape as truly missing rows so a USER cannot probe other
        # users' task IDs by status code.
        raise TaskError("Task not found", status_code=404)

    return task


def create_task(
    user: User,
    *,
    title: str,
    description: str | None = None,
    status: str = TaskStatus.PENDING.value,
) -> Task:
    task = Task(
        title=title.strip(),
        description=description,
        status=TaskStatus(status),
        user_id=user.id,
    )
    db.session.add(task)
    db.session.commit()
    logger.info("Created task id=%s user_id=%s", task.id, user.id)
    return task


def update_task(task_id: int, user: User, fields: dict[str, Any]) -> Task:
    task = get_task(task_id, user)

    if "title" in fields:
        task.title = fields["title"].strip()
    if "description" in fields:
        task.description = fields["description"]
    if "status" in fields:
        task.status = TaskStatus(fields["status"])

    db.session.commit()
    logger.info("Updated task id=%s by user_id=%s fields=%s", task.id, user.id, list(fields))
    return task


def delete_task(task_id: int, user: User) -> None:
    task = get_task(task_id, user)
    db.session.delete(task)
    db.session.commit()
    logger.info("Deleted task id=%s by user_id=%s", task_id, user.id)
