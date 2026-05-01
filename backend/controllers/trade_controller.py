from flask import request
from marshmallow import ValidationError

from ..middlewares import get_current_user
from ..schemas.trade_schema import TradeOrderSchema, TradeOutputSchema
from ..services import trade_service
from ..services.trade_service import TradeError
from ..utils.response import error_response, success_response

_order_schema = TradeOrderSchema()
_trade_schema = TradeOutputSchema()
_trade_many_schema = TradeOutputSchema(many=True)


def create_order_view():
    user = get_current_user()
    try:
        payload = _order_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return error_response("Validation failed", 400, details=err.messages)

    try:
        trade = trade_service.execute_order(
            user,
            symbol=payload["symbol"],
            side=payload["side"],
            type=payload["type"],
            quantity=payload["quantity"],
            price=payload.get("price"),
        )
    except TradeError as err:
        return error_response(
            err.message,
            err.status_code,
            details=err.details,
        )

    return success_response(
        data=_trade_schema.dump(trade),
        message="Trade executed",
        status_code=201,
    )


def history_view():
    user = get_current_user()
    symbol = request.args.get("symbol")
    status = request.args.get("status")
    limit_arg = request.args.get("limit", default="100")

    try:
        limit = int(limit_arg)
    except (TypeError, ValueError):
        return error_response(
            "Validation failed", 400,
            details={"limit": ["Must be an integer"]},
        )

    try:
        trades = trade_service.list_trade_history(
            user,
            symbol_filter=symbol,
            status_filter=status,
            limit=limit,
        )
    except TradeError as err:
        return error_response(err.message, err.status_code, details=err.details)

    return success_response(
        data=_trade_many_schema.dump(trades),
        message="Trade history fetched",
    )
