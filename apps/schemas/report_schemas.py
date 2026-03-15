from marshmallow import Schema, fields


class ReportCreateSchema(Schema):
    conversation_id = fields.Integer(required=True)
    title = fields.String(allow_none=True)
    content = fields.String(allow_none=True)


class ReportItemSchema(Schema):
    report_id = fields.Integer()
    conversation_id = fields.Integer()
    counselor_id = fields.Integer()
    user_id = fields.Integer()
    title = fields.String(allow_none=True)
    content = fields.String(allow_none=True)
    created_at = fields.String()
    delivered = fields.Boolean()
    delivered_at = fields.String(allow_none=True)


class ReportAttachmentSchema(Schema):
    filename = fields.String(allow_none=True)
    file_path = fields.String(allow_none=True)
    size = fields.Integer(allow_none=True)
    uploaded_at = fields.String(allow_none=True)
    public_url = fields.String(allow_none=True)


class ReportCreateResponseSchema(Schema):
    report = fields.Nested(ReportItemSchema)
    attachment = fields.Nested(ReportAttachmentSchema, allow_none=True)
