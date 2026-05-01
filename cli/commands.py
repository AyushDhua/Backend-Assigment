import json
import logging
import sys
from typing import Any

from backend.app import create_app
from backend.trading import (
    TradingConfigError,
    TradingExecutionError,
    TradingValidationError,
    place_order,
    validate_order_input,
)

# Exit codes — discoverable, scriptable.
EXIT_OK = 0
EXIT_EXCHANGE_REJECTED = 1
EXIT_VALIDATION_FAILED = 2
EXIT_NOT_CONFIGURED = 3


def cmd_place_order(
    *,
    symbol: Any,
    side: Any,
    type: Any,
    quantity: Any,
    price: Any = None,
    json_output: bool = False,
) -> int:
    """Run a single order through the trading module.

    Returns a process exit code so callers can branch on the outcome:
      0 success, 1 exchange rejection, 2 validation failure,
      3 module misconfiguration.
    """
    # Pre-validate so the request summary uses cleaned/normalized values
    # even when execution itself fails later.
    try:
        cleaned = validate_order_input(
            symbol=symbol, side=side, type=type, quantity=quantity, price=price
        )
    except TradingValidationError as exc:
        _emit_validation_error(exc.errors, json_output=json_output)
        return EXIT_VALIDATION_FAILED

    _emit_request_summary(cleaned, json_output=json_output)

    app = create_app()
    if json_output:
        _silence_stream_logs()

    with app.app_context():
        try:
            result = place_order(**cleaned)
        except TradingConfigError as exc:
            _emit_failure("config", str(exc), json_output=json_output)
            return EXIT_NOT_CONFIGURED
        except TradingExecutionError as exc:
            _emit_failure(
                "exchange",
                exc.message,
                exchange_code=exc.exchange_code,
                json_output=json_output,
            )
            return EXIT_EXCHANGE_REJECTED

    _emit_response(result, json_output=json_output)
    return EXIT_OK


# ---------- output helpers ---------------------------------------------------

def _emit_request_summary(cleaned: dict, *, json_output: bool) -> None:
    summary = {
        "symbol": cleaned["symbol"],
        "side": cleaned["side"],
        "type": cleaned["type"],
        "quantity": str(cleaned["quantity"]),
        "price": str(cleaned["price"]) if cleaned["price"] is not None else None,
    }

    if json_output:
        print(json.dumps({"phase": "request", "data": summary}))
        return

    print("=" * 50)
    print(" Request summary")
    print("=" * 50)
    for key in ("symbol", "side", "type", "quantity", "price"):
        value = summary[key]
        if value is None and key == "price":
            continue
        print(f"  {key:9s} : {value}")
    print()


def _emit_response(result: dict, *, json_output: bool) -> None:
    public = {k: v for k, v in result.items() if k != "raw"}

    if json_output:
        print(json.dumps({"phase": "response", "status": "success", "data": public}))
        return

    print("=" * 50)
    print(" Response")
    print("=" * 50)
    for key, value in public.items():
        print(f"  {key:18s} : {value}")
    print()
    print(
        f"SUCCESS  order_id={public.get('order_id')}  "
        f"status={public.get('status')}"
    )


def _emit_validation_error(errors: dict[str, str], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps({"phase": "validation", "status": "failure", "errors": errors}))
        return

    print("FAILURE  validation errors:", file=sys.stderr)
    for field, msg in errors.items():
        print(f"  {field}: {msg}", file=sys.stderr)


def _emit_failure(
    kind: str,
    message: str,
    *,
    exchange_code: int | str | None = None,
    json_output: bool,
) -> None:
    payload: dict = {
        "phase": "execution",
        "status": "failure",
        "kind": kind,
        "message": message,
    }
    if exchange_code is not None:
        payload["exchange_code"] = exchange_code

    if json_output:
        print(json.dumps(payload))
        return

    label = {"config": "CONFIG", "exchange": "EXCHANGE"}.get(kind, kind.upper())
    print(f"FAILURE  {label}: {message}", file=sys.stderr)
    if exchange_code is not None:
        print(f"  exchange_code: {exchange_code}", file=sys.stderr)


def _silence_stream_logs() -> None:
    """Keep CLI JSON output uncontaminated by app log lines."""
    root = logging.getLogger()
    for h in list(root.handlers):
        if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler):
            h.setLevel(logging.CRITICAL)
