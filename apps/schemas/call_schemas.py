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
    call_type = fields.String()
    status = fields.String()
    created_at = fields.String()
    started_at = fields.String(allow_none=True)
    ended_at = fields.String(allow_none=True)
    ended_reason = fields.String(allow_none=True)
    metadata = fields.String(allow_none=True)


class CallParticipantSchema(Schema):
    call_participant_id = fields.Integer()
    call_session_id = fields.Integer()
    participant_user_id = fields.Integer(allow_none=True)
    participant_counselor_id = fields.Integer(allow_none=True)
    role = fields.String()
    status = fields.String()
    joined_at = fields.String(allow_none=True)
    left_at = fields.String(allow_none=True)
    created_at = fields.String()


class CallSessionListItemSchema(Schema):
    call_session = fields.Nested(CallSessionSchema)
    participant = fields.Nested(CallParticipantSchema)
