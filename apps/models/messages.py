from datetime import datetime
from peewee import (
    AutoField,
    TextField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    BooleanField,
    SQL,
)


class Message:
    message_id = AutoField()
    conversation = ForeignKeyField(
        "Conversation", backref="messages", column_name="conversation_id"
    )
    sender_user = ForeignKeyField(
        "User", null=True, backref="sent_messages", column_name="sender_user_id"
    )
    sender_counselor = ForeignKeyField(
        "Counselor",
        null=True,
        backref="sent_messages",
        column_name="sender_counselor_id",
    )
    content = TextField(null=True)
    content_type = CharField(default="text")
    created_at = DateTimeField(default=datetime.utcnow)
    edited_at = DateTimeField(null=True)
    reply_to = ForeignKeyField(
        "self", null=True, backref="replies", column_name="reply_to"
    )
    deleted = BooleanField(default=False)

    class Meta:
        table_name = "messages"
        indexes = ((("conversation", "created_at"), False),)
        constraints = [
            SQL(
                "((sender_user_id IS NOT NULL)::int + (sender_counselor_id IS NOT NULL)::int) = 1"
            )
        ]
