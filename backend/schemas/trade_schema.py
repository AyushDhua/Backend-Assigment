from marshmallow import Schema, fields, validate


class TradeOrderSchema(Schema):
    """HTTP-layer envelope check for ``POST /api/v1/trades/order``.

    All value-shape rules (allowed sides/types, LIMIT-needs-price,
    quantity > 0, symbol format, case-normalization) live in
    ``backend.trading.validators`` so the CLI and HTTP layer apply identical
    rules. The schema's job is only to confirm required keys are present.
    """

    symbol = fields.String(required=True, validate=validate.Length(min=1, max=20))
    side = fields.String(required=True, validate=validate.Length(min=1, max=8))
    type = fields.String(required=True, validate=validate.Length(min=1, max=10))
    # quantity / price stay as Raw so the trading-module validators get to
    # coerce them into Decimal — JSON numbers would otherwise lose precision.
    quantity = fields.Raw(required=True)
    price = fields.Raw(load_default=None, allow_none=True)


class TradeOutputSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    symbol = fields.String(dump_only=True)
    side = fields.Method("dump_side", dump_only=True)
    type = fields.Method("dump_type", dump_only=True)
    quantity = fields.Decimal(as_string=True, dump_only=True)
    price = fields.Decimal(as_string=True, dump_only=True, allow_none=True)
    status = fields.Method("dump_status", dump_only=True)
    order_id = fields.String(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    def dump_side(self, obj) -> str | None:
        return obj.side.value if obj.side is not None else None

    def dump_type(self, obj) -> str | None:
        return obj.order_type.value if obj.order_type is not None else None

    def dump_status(self, obj) -> str | None:
        return obj.status.value if obj.status is not None else None
