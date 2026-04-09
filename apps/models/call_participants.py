from datetime import datetime
from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, SQL


class CallParticipant:
    call_participant_id = AutoField()
    call_session = ForeignKeyField(
        "CallSession", backref="participants", column_name="call_session_id"
    )
    participant_user = ForeignKeyField(
        "User", null=True, backref="call_participations", column_name="participant_user_id"
    )
    participant_counselor = ForeignKeyField(
        "Counselor",
        null=True,
        backref="call_participations",
        column_name="participant_counselor_id",
    )
    role = CharField(default="callee")
    status = CharField(default="ringing")
    joined_at = DateTimeField(null=True)
    left_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "call_participants"
        indexes = (("call_session", "created_at"), False)
        constraints = [
            SQL(
                "((participant_user_id IS NOT NULL)::int + (participant_counselor_id IS NOT NULL)::int) = 1"
            )
        ]
