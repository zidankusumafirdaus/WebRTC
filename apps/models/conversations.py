from datetime import datetime
from peewee import AutoField, DateTimeField, ForeignKeyField, CharField, IntegerField, TextField


class Conversation:
    conversation_id = AutoField()
    user = ForeignKeyField("User", backref="conversations", column_name="user_id")
    counselor = ForeignKeyField(
        "Counselor", backref="conversations", column_name="counselor_id"
    )
    request_status = CharField(null=True)
    requested_at = DateTimeField(null=True)
    scheduled_at = DateTimeField(null=True)
    duration_minutes = IntegerField(null=True)
    expires_at = DateTimeField(null=True)
    responded_at = DateTimeField(null=True)
    response_message = TextField(null=True)
    cancelled_at = DateTimeField(null=True)
    cancelled_by = CharField(null=True)
    cancel_reason = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "conversations"
        indexes = ((("user", "counselor"), True),)
