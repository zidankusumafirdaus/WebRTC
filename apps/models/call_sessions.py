from datetime import datetime
from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, TextField, SQL


class CallSession:
    call_session_id = AutoField()
    conversation = ForeignKeyField(
        "Conversation", null=True, backref="call_sessions", column_name="conversation_id"
    )
    initiator_user = ForeignKeyField(
        "User", null=True, backref="initiated_calls", column_name="initiator_user_id"
    )
    initiator_counselor = ForeignKeyField(
        "Counselor",
        null=True,
        backref="initiated_calls",
        column_name="initiator_counselor_id",
    )
    call_type = CharField(default="audio")
    status = CharField(default="initiated")
    created_at = DateTimeField(default=datetime.utcnow)
    started_at = DateTimeField(null=True)
    ended_at = DateTimeField(null=True)
    ended_reason = CharField(null=True)
    metadata = TextField(null=True)

    class Meta:
        table_name = "call_sessions"
        indexes = (("conversation", "created_at"), False)
        constraints = [
            SQL(
                "((initiator_user_id IS NOT NULL)::int + (initiator_counselor_id IS NOT NULL)::int) = 1"
            )
        ]
