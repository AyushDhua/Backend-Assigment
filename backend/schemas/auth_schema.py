from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    # bcrypt only considers the first 72 bytes of input — cap input length here
    # so the contract is explicit instead of relying on silent truncation.
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=72),
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class UserPublicSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.Method("dump_role", dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    def dump_role(self, obj) -> str:
        return obj.role.value if obj.role is not None else None
