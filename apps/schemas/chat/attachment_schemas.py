from marshmallow import Schema, fields
from apps.schemas.chat.chat_schemas import MessageSchema


class AttachmentSchema(Schema):
    filename = fields.String()
    file_path = fields.String()
    public_url = fields.String()


class SendAttachmentResponseSchema(Schema):
    message = fields.Nested(MessageSchema)
    attachment = fields.Nested(AttachmentSchema)
