import logging
from typing import Any

from binance.enums import (
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
    SIDE_BUY,
    SIDE_SELL,
    TIME_IN_FORCE_GTC,
)
from binance.exceptions import BinanceAPIException, BinanceOrderException

from .client import get_client
from .utils import TradingExecutionError, format_decimal, normalize_order_response
from .validators import validate_order_input

logger = logging.getLogger(__name__)

_SIDE_MAP = {"BUY": SIDE_BUY, "SELL": SIDE_SELL}
_TYPE_MAP = {"MARKET": ORDER_TYPE_MARKET, "LIMIT": ORDER_TYPE_LIMIT}


def place_order(
    *,
    symbol: str,
    side: str,
    type: str,
    quantity: Any,
    price: Any = None,
) -> dict:
    """Validate input and submit a futures order to Binance Testnet.

    Returns a normalized order dict (see ``utils.normalize_order_response``).

    Raises:
        TradingValidationError: input failed validation.
        TradingConfigError:     module is not configured.
        TradingExecutionError:  Binance rejected or failed to process the order.
    """
    cleaned = validate_order_input(
        symbol=symbol, side=side, type=type, quantity=quantity, price=price
    )

    params: dict[str, Any] = {
        "symbol": cleaned["symbol"],
        "side": _SIDE_MAP[cleaned["side"]],
        "type": _TYPE_MAP[cleaned["type"]],
        "quantity": format_decimal(cleaned["quantity"]),
    }
    if cleaned["type"] == "LIMIT":
        params["price"] = format_decimal(cleaned["price"])
        params["timeInForce"] = TIME_IN_FORCE_GTC

    client = get_client()

    log_params = {**params, "_quantity_decimal": str(cleaned["quantity"])}
    logger.info("Submitting Binance futures order: %s", log_params)

    from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
    import requests

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type((BinanceAPIException, requests.exceptions.RequestException)),
        reraise=True
    )
    def _execute(client, params):
        return client.futures_create_order(timeout=5, **params)

    try:
        response = _execute(client, params)
    except requests.exceptions.RequestException as exc:
        logger.error("Binance network/timeout error: %s", exc)
        raise TradingExecutionError("External API unavailable") from exc
    except BinanceAPIException as exc:
        logger.error("Binance API error code=%s msg=%s", exc.code, exc.message)
        raise TradingExecutionError(exc.message, exchange_code=exc.code) from exc
    except BinanceOrderException as exc:
        logger.error("Binance order error code=%s msg=%s", exc.code, exc.message)
        raise TradingExecutionError(exc.message, exchange_code=exc.code) from exc

    normalized = normalize_order_response(response)
    logger.info(
        "Order placed orderId=%s status=%s",
        normalized.get("order_id"), normalized.get("status"),
    )
    return normalized
