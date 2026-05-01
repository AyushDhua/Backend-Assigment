import re
from decimal import Decimal, InvalidOperation
from typing import Any

from .utils import TradingValidationError

VALID_SIDES = ("BUY", "SELL")
VALID_TYPES = ("MARKET", "LIMIT")

_SYMBOL_RE = re.compile(r"^[A-Z0-9]{5,20}$")


def _coerce_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def validate_order_input(
    *,
    symbol: Any,
    side: Any,
    type: Any,
    quantity: Any,
    price: Any = None,
) -> dict[str, Any]:
    """Validate and normalize order parameters.

    Returns a dict with cleaned values:
      ``symbol`` (str, uppercase), ``side``, ``type`` (uppercase),
      ``quantity`` (Decimal), ``price`` (Decimal | None).

    Raises ``TradingValidationError`` with per-field messages otherwise.
    """
    errors: dict[str, str] = {}

    # symbol -----------------------------------------------------------------
    cleaned_symbol: str | None = None
    if not isinstance(symbol, str) or not symbol.strip():
        errors["symbol"] = "Symbol is required"
    else:
        candidate = symbol.strip().upper()
        if not _SYMBOL_RE.fullmatch(candidate):
            errors["symbol"] = "Must be 5-20 uppercase alphanumeric characters (e.g. BTCUSDT)"
        else:
            cleaned_symbol = candidate

    # side -------------------------------------------------------------------
    cleaned_side: str | None = None
    if not isinstance(side, str):
        errors["side"] = f"Must be one of {list(VALID_SIDES)}"
    else:
        candidate = side.strip().upper()
        if candidate not in VALID_SIDES:
            errors["side"] = f"Must be one of {list(VALID_SIDES)}"
        else:
            cleaned_side = candidate

    # type -------------------------------------------------------------------
    cleaned_type: str | None = None
    if not isinstance(type, str):
        errors["type"] = f"Must be one of {list(VALID_TYPES)}"
    else:
        candidate = type.strip().upper()
        if candidate not in VALID_TYPES:
            errors["type"] = f"Must be one of {list(VALID_TYPES)}"
        else:
            cleaned_type = candidate

    # quantity ---------------------------------------------------------------
    qty = _coerce_decimal(quantity)
    if qty is None:
        errors["quantity"] = "Must be a valid number"
    elif qty <= 0:
        errors["quantity"] = "Must be greater than 0"

    # price ------------------------------------------------------------------
    cleaned_price: Decimal | None = None
    if cleaned_type == "LIMIT":
        if price is None or (isinstance(price, str) and not price.strip()):
            errors["price"] = "Price is required for LIMIT orders"
        else:
            p = _coerce_decimal(price)
            if p is None:
                errors["price"] = "Must be a valid number"
            elif p <= 0:
                errors["price"] = "Must be greater than 0"
            else:
                cleaned_price = p
    elif cleaned_type == "MARKET" and price not in (None, ""):
        errors["price"] = "Price must not be provided for MARKET orders"

    if errors:
        raise TradingValidationError(errors)

    return {
        "symbol": cleaned_symbol,
        "side": cleaned_side,
        "type": cleaned_type,
        "quantity": qty,
        "price": cleaned_price,
    }
