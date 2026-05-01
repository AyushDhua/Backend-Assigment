from marshmallow import Schema, fields, validate

from ..models import TaskStatus

_STATUS_VALUES = [s.value for s in TaskStatus]


class TaskCreateSchema(Schema):
    title = fields.String(
        required=True, validate=validate.Length(min=1, max=255)
    )
    description = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=10_000),
    )
    status = fields.String(
        load_default=TaskStatus.PENDING.value,
        validate=validate.OneOf(_STATUS_VALUES),
    )


class TaskUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=255))
    description = fields.String(
        allow_none=True, validate=validate.Length(max=10_000)
    )
    status = fields.String(validate=validate.OneOf(_STATUS_VALUES))


class TaskOutputSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(dump_only=True)
    description = fields.String(dump_only=True)
    status = fields.Method("dump_status", dump_only=True)
    user_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    def dump_status(self, obj) -> str | None:
        return obj.status.value if obj.status is not None else None
