from marshmallow import Schema, fields


class CallStartRequestSchema(Schema):
    conversation_id = fields.Integer(required=True)
    call_type = fields.String(load_default="audio")


class CallEndRequestSchema(Schema):
    ended_reason = fields.String(allow_none=True)


class CallSessionSchema(Schema):
    call_session_id = fields.Integer()
    conversation_id = fields.Integer(allow_none=True)
    initiator_user_id = fields.Integer(allow_none=True)
    initiator_counselor_id = fields.Integer(allow_none=True)
    participant_user_id = fields.Integer(allow_none=True)
    participant_counselor_id = fields.Integer(allow_none=True)
    call_type = fields.String()
    status = fields.String()
    created_at = fields.String()
    started_at = fields.String(allow_none=True)
    ended_at = fields.String(allow_none=True)
    ended_reason = fields.String(allow_none=True)
    metadata = fields.String(allow_none=True)
    participant_user_status = fields.String(allow_none=True)
    participant_counselor_status = fields.String(allow_none=True)
    participant_user_joined_at = fields.String(allow_none=True)
    participant_counselor_joined_at = fields.String(allow_none=True)
    participant_user_left_at = fields.String(allow_none=True)
    participant_counselor_left_at = fields.String(allow_none=True)
