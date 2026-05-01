import logging
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import select

from ..extensions import db
from ..middlewares import filter_for_current_user
from ..models import Trade, TradeSide, TradeStatus, TradeType, User
from ..trading import (
    TradingConfigError,
    TradingExecutionError,
    TradingValidationError,
    place_order,
    validate_order_input,
)

logger = logging.getLogger(__name__)


class TradeError(Exception):
    """Service-layer error mapped to an HTTP response by the controller."""

    def __init__(self, message: str, status_code: int = 400, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def _safe_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return d if d > 0 else None


def _persist_trade(
    *,
    user: User,
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Decimal | None,
    status: TradeStatus,
    order_id: str | None,
) -> Trade:
    trade = Trade(
        user_id=user.id,
        symbol=symbol,
        side=TradeSide(side),
        order_type=TradeType(order_type),
        quantity=quantity,
        price=price,
        status=status,
        order_id=order_id,
    )
    db.session.add(trade)
    db.session.commit()
    return trade


def execute_order(
    user: User,
    *,
    symbol: Any,
    side: Any,
    type: Any,
    quantity: Any,
    price: Any = None,
) -> Trade:
    """Validate, submit to Binance, and persist a Trade row.

    Raises ``TradeError`` with an HTTP-friendly status code:
      400 — input validation or exchange rejection
      503 — module misconfiguration (missing API credentials)
    """
    # Pre-validate so we have cleaned values for the rejection-persist path.
    try:
        cleaned = validate_order_input(
            symbol=symbol, side=side, type=type, quantity=quantity, price=price
        )
    except TradingValidationError as exc:
        raise TradeError("Validation failed", 400, details=exc.errors) from exc

    try:
        result = place_order(
            symbol=cleaned["symbol"],
            side=cleaned["side"],
            type=cleaned["type"],
            quantity=cleaned["quantity"],
            price=cleaned["price"],
        )
    except TradingConfigError as exc:
        raise TradeError(str(exc), 503) from exc
    except TradingExecutionError as exc:
        # Exchange rejected the order. Persist a REJECTED row so the user
        # sees the attempt in their history alongside successful trades.
        rejected = _persist_trade(
            user=user,
            symbol=cleaned["symbol"],
            side=cleaned["side"],
            order_type=cleaned["type"],
            quantity=cleaned["quantity"],
            price=cleaned["price"],
            status=TradeStatus.REJECTED,
            order_id=None,
        )
        logger.warning(
            "Trade rejected by exchange trade_id=%s code=%s msg=%s",
            rejected.id, exc.exchange_code, exc.message,
        )
        raise TradeError(
            "Trade rejected by exchange",
            status_code=400,
            details={
                "exchange_code": exc.exchange_code,
                "exchange_message": exc.message,
                "trade_id": rejected.id,
            },
        ) from exc

    # Success — translate the normalized exchange response to a Trade row.
    raw_status = result.get("status") or "NEW"
    try:
        status_enum = TradeStatus(raw_status)
    except ValueError:
        # Unknown Binance status — preserve the order but mark as NEW.
        logger.warning("Unrecognised exchange status %r, defaulting to NEW", raw_status)
        status_enum = TradeStatus.NEW

    exec_qty = _safe_decimal(result.get("quantity")) or cleaned["quantity"]
    avg_price = _safe_decimal(result.get("average_price"))
    declared_price = _safe_decimal(result.get("price"))
    final_price = avg_price or declared_price or cleaned["price"]

    trade = _persist_trade(
        user=user,
        symbol=result.get("symbol") or cleaned["symbol"],
        side=result.get("side") or cleaned["side"],
        order_type=result.get("type") or cleaned["type"],
        quantity=exec_qty,
        price=final_price,
        status=status_enum,
        order_id=result.get("order_id"),
    )
    logger.info(
        "Trade persisted id=%s user_id=%s order_id=%s status=%s",
        trade.id, user.id, trade.order_id, trade.status.value,
    )
    return trade


def list_trade_history(
    user: User,
    *,
    symbol_filter: str | None = None,
    status_filter: str | None = None,
    limit: int = 100,
) -> list[Trade]:
    """Return trade history scoped to the user (ADMIN sees everything)."""
    stmt = select(Trade).order_by(Trade.created_at.desc())
    stmt = filter_for_current_user(stmt, Trade.user_id, user=user)

    if symbol_filter:
        stmt = stmt.where(Trade.symbol == symbol_filter.strip().upper())

    if status_filter:
        try:
            stmt = stmt.where(Trade.status == TradeStatus(status_filter.strip().upper()))
        except ValueError:
            raise TradeError(
                f"Unknown status '{status_filter}'", status_code=400
            )

    stmt = stmt.limit(max(1, min(limit, 500)))
    return list(db.session.execute(stmt).scalars().all())
