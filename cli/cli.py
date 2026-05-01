"""CLI entry point for placing Binance Futures Testnet orders.

Usage examples
--------------
From the project root, either:

    python -m cli.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

    python cli/cli.py --symbol BTCUSDT --side BUY --type LIMIT \\
        --quantity 0.01 --price 65000

Add ``--json`` for machine-readable output (one JSON object per phase).

Exit codes
----------
    0  success
    1  exchange rejection
    2  input validation failed
    3  trading module not configured (missing API credentials)
"""

import argparse
import sys
from pathlib import Path

# Allow ``python cli/cli.py`` and ``python cli.py`` to find the project root.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cli.commands import cmd_place_order  # noqa: E402  (after sys.path tweak)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description=(
            "Place a Binance Futures Testnet order via the shared trading "
            "module. The same validators and client used by the HTTP API."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m cli.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01\n"
            "  python -m cli.cli --symbol ETHUSDT --side SELL --type LIMIT "
            "--quantity 0.5 --price 3000\n"
        ),
    )
    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair (e.g. BTCUSDT). Case-insensitive.",
    )
    parser.add_argument(
        "--side", required=True,
        help="Order side: BUY or SELL (case-insensitive).",
    )
    parser.add_argument(
        "--type", required=True,
        help="Order type: MARKET or LIMIT (case-insensitive).",
    )
    parser.add_argument(
        "--quantity", required=True,
        help="Order quantity, e.g. 0.01. Must be > 0.",
    )
    parser.add_argument(
        "--price", default=None,
        help="Required for LIMIT orders, omitted for MARKET orders.",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Emit machine-readable JSON output (one object per phase).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return cmd_place_order(
        symbol=args.symbol,
        side=args.side,
        type=args.type,
        quantity=args.quantity,
        price=args.price,
        json_output=args.json_output,
    )


if __name__ == "__main__":
    sys.exit(main())
