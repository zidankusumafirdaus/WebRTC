from marshmallow import Schema, fields

class UserProfileSchema(Schema):
    user_id = fields.Integer()
    username = fields.String()
    display_name = fields.String(allow_none=True)
    created_at = fields.String(allow_none=True)
    conversation_count = fields.Integer()
    unique_counselors_count = fields.Integer()
    messages_sent_count = fields.Integer()
    reports_received_count = fields.Integer()
    last_active = fields.String(allow_none=True)
    updated_at = fields.String(allow_none=True)

class CounselorProfileSchema(Schema):
    counselor_id = fields.Integer()
    username = fields.String()
    display_name = fields.String(allow_none=True)
    bio = fields.String(allow_none=True)
    qualifications = fields.String(allow_none=True)
    created_at = fields.String(allow_none=True)
    conversation_count = fields.Integer()
    unique_users_count = fields.Integer()
    messages_sent_count = fields.Integer()
    reports_created_count = fields.Integer()
    accepted_requests_count = fields.Integer()
    last_active = fields.String(allow_none=True)
    updated_at = fields.String(allow_none=True)
