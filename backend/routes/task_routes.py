from flask import Blueprint

from ..controllers import task_controller
from ..middlewares import auth_required

task_bp = Blueprint("tasks", __name__)


@task_bp.get("")
@auth_required
def list_tasks():
    return task_controller.list_tasks_view()


@task_bp.post("")
@auth_required
def create_task():
    return task_controller.create_task_view()


@task_bp.put("/<int:task_id>")
@auth_required
def update_task(task_id: int):
    return task_controller.update_task_view(task_id)


@task_bp.delete("/<int:task_id>")
@auth_required
def delete_task(task_id: int):
    return task_controller.delete_task_view(task_id)
