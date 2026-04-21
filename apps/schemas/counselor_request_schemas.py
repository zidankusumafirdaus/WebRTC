from marshmallow import Schema, fields


class CounselorListSchema(Schema):
    counselor_id = fields.Integer()
    display_name = fields.String()
    bio = fields.String(allow_none=True)
    qualifications = fields.String(allow_none=True)


class RequestCounselorSchema(Schema):
    counselor_id = fields.Integer(required=True)
    message = fields.String(allow_none=True)
    scheduled_at = fields.DateTime(allow_none=True)
    duration_minutes = fields.Integer(allow_none=True)


class RequestResponseSchema(Schema):
    message = fields.String()
    conversation_id = fields.Integer()


class CancelRequestSchema(Schema):
    conversation_id = fields.Integer(required=True)
    cancel_reason = fields.String(allow_none=True)


class RespondRequestSchema(Schema):
    conversation_id = fields.Integer(required=True)
    status = fields.String(
        required=True, validate=lambda x: x in ["accepted", "rejected"]
    )


class RequestListSchema(Schema):
    conversation_id = fields.Integer()
    user_id = fields.Integer()
    message = fields.String()
    requested_at = fields.String()
    expires_at = fields.String()
    scheduled_at = fields.String(allow_none=True)
    duration_minutes = fields.Integer(allow_none=True)


class ReportSchema(Schema):
    report_id = fields.Integer()
    user_id = fields.Integer()
    title = fields.String()
    content = fields.String()
    created_at = fields.String()


class UserRequestSummarySchema(Schema):
    conversation_id = fields.Integer()
    counselor_id = fields.Integer()
    counselor_name = fields.String(allow_none=True)
    status = fields.String()
    requested_at = fields.String()
    expires_at = fields.String(allow_none=True)
    responded_at = fields.String(allow_none=True)
    scheduled_at = fields.String(allow_none=True)
    duration_minutes = fields.Integer(allow_none=True)
