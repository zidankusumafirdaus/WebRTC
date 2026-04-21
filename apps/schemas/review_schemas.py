from marshmallow import Schema, fields, validate


class ReviewCreateSchema(Schema):
    target_counselor_id = fields.Integer(required=True)
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.String(allow_none=True)
    session_id = fields.Integer(allow_none=True)


class ReviewItemSchema(Schema):
    review_id = fields.Integer()
    session_id = fields.Integer(allow_none=True)
    reviewer_user_id = fields.Integer(allow_none=True)
    reviewer_counselor_id = fields.Integer(allow_none=True)
    target_user_id = fields.Integer(allow_none=True)
    target_counselor_id = fields.Integer(allow_none=True)
    rating = fields.Integer(allow_none=True)
    comment = fields.String(allow_none=True)
    created_at = fields.String()
