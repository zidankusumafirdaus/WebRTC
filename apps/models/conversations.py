from datetime import datetime
from peewee import AutoField, DateTimeField, ForeignKeyField


class Conversation:
    conversation_id = AutoField()
    user = ForeignKeyField("User", backref="conversations", column_name="user_id")
    counselor = ForeignKeyField(
        "Counselor", backref="conversations", column_name="counselor_id"
    )
    request = ForeignKeyField(
        "CounselorRequest", null=True, backref="conversation", column_name="request_id"
    )
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "conversations"
        indexes = ((("user", "counselor"), True),)
