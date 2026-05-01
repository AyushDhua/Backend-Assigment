from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .user_model import User


class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TradeStatus(str, Enum):
    PENDING = "PENDING"
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Trade(db.Model):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    side: Mapped[TradeSide] = mapped_column(
        SqlEnum(
            TradeSide,
            name="trade_side",
            native_enum=False,
            length=8,
            validate_strings=True,
        ),
        nullable=False,
    )

    # `type` shadows a Python builtin, so the attribute is `order_type`
    # while the database column keeps the PRD-mandated name `type`.
    order_type: Mapped[TradeType] = mapped_column(
        "type",
        SqlEnum(
            TradeType,
            name="trade_type",
            native_enum=False,
            length=10,
            validate_strings=True,
        ),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)

    price: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)

    status: Mapped[TradeStatus] = mapped_column(
        SqlEnum(
            TradeStatus,
            name="trade_status",
            native_enum=False,
            length=20,
            validate_strings=True,
        ),
        nullable=False,
        default=TradeStatus.PENDING,
        server_default=TradeStatus.PENDING.value,
        index=True,
    )

    order_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="trades")

    def __repr__(self) -> str:
        return (
            f"<Trade id={self.id} user_id={self.user_id} symbol={self.symbol} "
            f"side={self.side.value} type={self.order_type.value} "
            f"qty={self.quantity} price={self.price} "
            f"status={self.status.value} order_id={self.order_id}>"
        )
