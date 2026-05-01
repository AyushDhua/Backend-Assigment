import logging

from binance.client import Client
from flask import current_app

from .utils import TradingConfigError

logger = logging.getLogger(__name__)

_EXTENSIONS_KEY = "binance_client"


def get_client() -> Client:
    """Return a process-cached Binance ``Client`` configured from app config.

    Reads ``BINANCE_API_KEY`` / ``BINANCE_API_SECRET`` / ``BINANCE_TESTNET``
    from ``current_app.config`` and caches the instance on
    ``app.extensions['binance_client']``.

    Raises ``TradingConfigError`` if credentials are not configured.
    """
    app = current_app._get_current_object()

    cached = app.extensions.get(_EXTENSIONS_KEY)
    if cached is not None:
        return cached

    api_key = (app.config.get("BINANCE_API_KEY") or "").strip()
    api_secret = (app.config.get("BINANCE_API_SECRET") or "").strip()
    testnet = bool(app.config.get("BINANCE_TESTNET", True))

    if not api_key or not api_secret:
        raise TradingConfigError(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set in the "
            "environment before placing orders."
        )

    client = Client(api_key, api_secret, testnet=testnet)
    app.extensions[_EXTENSIONS_KEY] = client

    logger.info(
        "Initialized Binance %s client (futures URL=%s)",
        "TESTNET" if testnet else "MAINNET",
        client.FUTURES_URL,
    )
    return client


def reset_client() -> None:
    """Drop the cached client. Useful for tests and credential rotation."""
    app = current_app._get_current_object()
    app.extensions.pop(_EXTENSIONS_KEY, None)
