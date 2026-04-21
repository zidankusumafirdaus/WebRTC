from datetime import datetime
from enum import Enum
from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, IntegerField, TextField
from playhouse.postgres_ext import EnumField


class CounselingSessionStatus(Enum):
    scheduled = "scheduled"
    in_session = "in_session"
    completed = "completed"
    cancelled = "cancelled"
    no_show_user = "no_show_user"
    no_show_counselor = "no_show_counselor"
    expired = "expired"


class CounselingSession:
    session_id = AutoField()
    conversation = ForeignKeyField(
        "Conversation", null=True, backref="sessions", column_name="conversation_id"
    )
    user = ForeignKeyField("User", backref="sessions", column_name="user_id")
    counselor = ForeignKeyField(
        "Counselor", backref="sessions", column_name="counselor_id"
    )
    status = EnumField(CounselingSessionStatus, null=True)
    scheduled_start = DateTimeField(null=True)
    duration_minutes = IntegerField(null=True)
    actual_start = DateTimeField(null=True)
    actual_end = DateTimeField(null=True)
    extended_minutes = IntegerField(default=0)
    cancelled_at = DateTimeField(null=True)
    cancelled_by = CharField(null=True)
    cancel_reason = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "counseling_sessions"
        indexes = (
            (("user", "counselor"), False),
            (("status", "scheduled_start"), False),
        )
