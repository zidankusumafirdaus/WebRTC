from datetime import datetime
from peewee import AutoField, DateTimeField, ForeignKeyField, IntegerField, TextField, SQL


class Review:
    review_id = AutoField()
    session = ForeignKeyField(
        "CounselingSession", null=True, backref="reviews", column_name="session_id"
    )
    reviewer_user = ForeignKeyField(
        "User", null=True, backref="reviews_made", column_name="reviewer_user_id"
    )
    reviewer_counselor = ForeignKeyField(
        "Counselor",
        null=True,
        backref="reviews_made",
        column_name="reviewer_counselor_id",
    )
    target_user = ForeignKeyField(
        "User", null=True, backref="reviews_received", column_name="target_user_id"
    )
    target_counselor = ForeignKeyField(
        "Counselor",
        null=True,
        backref="reviews_received",
        column_name="target_counselor_id",
    )
    rating = IntegerField(null=True)
    comment = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "reviews"
        indexes = (
            (("session",), False),
            (("target_user",), False),
            (("target_counselor",), False),
        )
        constraints = [
            SQL(
                "((reviewer_user_id IS NOT NULL)::int + (reviewer_counselor_id IS NOT NULL)::int) = 1"
            ),
            SQL(
                "((target_user_id IS NOT NULL)::int + (target_counselor_id IS NOT NULL)::int) = 1"
            ),
        ]
