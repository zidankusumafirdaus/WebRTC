from marshmallow import Schema, fields

class ConversationItemSchema(Schema):
    conversation_id = fields.Integer()
    user_id = fields.Integer()
    counselor_id = fields.Integer()
    created_at = fields.String(allow_none=True)
    counterparty_name = fields.String(allow_none=True)

class MessageSchema(Schema):
    message_id = fields.Integer()
    conversation_id = fields.Integer()
    sender_user_id = fields.Integer(allow_none=True)
    sender_counselor_id = fields.Integer(allow_none=True)
    content = fields.String()
    content_type = fields.String()
    created_at = fields.String()
    reply_to = fields.Integer(allow_none=True)
    deleted = fields.Boolean()

class SendMessageRequestSchema(Schema):
    conversation_id = fields.Integer(required=True)
    content = fields.String(required=True)
    content_type = fields.String(load_default="text")
    reply_to = fields.Integer(allow_none=True)

class MarkReadRequestSchema(Schema):
    message_ids = fields.List(fields.Integer(), required=True)

class UpdateMessageRequestSchema(Schema):
    content = fields.String(required=True)
    content_type = fields.String(load_default="text")
