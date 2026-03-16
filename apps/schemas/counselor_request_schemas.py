from marshmallow import Schema, fields


class CounselorListSchema(Schema):
    counselor_id = fields.Integer()
    display_name = fields.String()
    bio = fields.String(allow_none=True)
    qualifications = fields.String(allow_none=True)


class RequestCounselorSchema(Schema):
    counselor_id = fields.Integer(required=True)
    message = fields.String(allow_none=True)


class RequestResponseSchema(Schema):
    message = fields.String()
    request_id = fields.Integer()


class RespondRequestSchema(Schema):
    request_id = fields.Integer(required=True)
    status = fields.String(
        required=True, validate=lambda x: x in ["accepted", "rejected"]
    )


class RequestListSchema(Schema):
    request_id = fields.Integer()
    user_id = fields.Integer()
    message = fields.String()
    requested_at = fields.String()
    expires_at = fields.String()


class ReportSchema(Schema):
    report_id = fields.Integer()
    user_id = fields.Integer()
    title = fields.String()
    content = fields.String()
    created_at = fields.String()


class UserRequestSummarySchema(Schema):
    request_id = fields.Integer()
    counselor_id = fields.Integer()
    counselor_name = fields.String(allow_none=True)
    status = fields.String()
    requested_at = fields.String()
    expires_at = fields.String(allow_none=True)
    responded_at = fields.String(allow_none=True)
