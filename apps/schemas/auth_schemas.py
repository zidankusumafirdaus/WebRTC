from marshmallow import Schema, fields

class LoginRequestSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

class RegisterUserSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    display_name = fields.String(required=True)

class RegisterCounselorSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    display_name = fields.String(required=True)
    bio = fields.String(allow_none=True)
    qualifications = fields.String(allow_none=True)

class LoginResponseSchema(Schema):
    access_token = fields.String()
    user_id = fields.String()
    role = fields.String()
    display_name = fields.String(allow_none=True)

class RegisterResponseSchema(Schema):
    message = fields.String()
    user_id = fields.String()

class LogoutResponseSchema(Schema):
    message = fields.String()