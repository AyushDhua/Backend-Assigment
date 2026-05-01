from decimal import Decimal


class TradingError(Exception):
    """Base class for any trading-module failure."""


class TradingValidationError(TradingError):
    """Raised when caller-supplied order parameters fail validation."""

    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__("Trading input validation failed")


class TradingExecutionError(TradingError):
    """Raised when the exchange rejects or fails to process an order."""

    def __init__(self, message: str, exchange_code: int | str | None = None):
        self.message = message
        self.exchange_code = exchange_code
        super().__init__(message)


class TradingConfigError(TradingError):
    """Raised when the module is not configured (missing API credentials)."""


def format_decimal(value: Decimal | int | float | str) -> str:
    """Render a numeric value as a clean fixed-point string for the Binance API.

    Avoids scientific notation (``1E-3``) which Binance rejects, and strips
    trailing zeros for cleaner request payloads.
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    s = format(value, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def normalize_order_response(response: dict) -> dict:
    """Project Binance's verbose order dict into the fields we care about."""
    return {
        "order_id": str(response.get("orderId")) if response.get("orderId") is not None else None,
        "client_order_id": response.get("clientOrderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
        "status": response.get("status"),
        "quantity": response.get("origQty"),
        "executed_quantity": response.get("executedQty"),
        "price": response.get("price"),
        "average_price": response.get("avgPrice"),
        "time_in_force": response.get("timeInForce"),
        "raw": response,
    }
