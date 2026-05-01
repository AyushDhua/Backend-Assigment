from flask import Blueprint

from ..controllers import trade_controller
from ..middlewares import auth_required

trade_bp = Blueprint("trades", __name__)


@trade_bp.post("/order")
@auth_required
def create_order():
    return trade_controller.create_order_view()


@trade_bp.get("/history")
@auth_required
def history():
    return trade_controller.history_view()
