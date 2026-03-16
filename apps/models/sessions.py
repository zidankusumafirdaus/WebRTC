from datetime import datetime
from peewee import AutoField, CharField, DateTimeField, TextField, ForeignKeyField


class Session:
    sessions_id = AutoField()
    user = ForeignKeyField("User", null=True, backref="sessions", column_name="user_id")
    counselor = ForeignKeyField(
        "Counselor", null=True, backref="sessions", column_name="counselor_id"
    )
    socket_id = CharField(null=True)
    connected_at = DateTimeField(default=datetime.utcnow)
    disconnected_at = DateTimeField(null=True)
    device_info = TextField(null=True)

    class Meta:
        table_name = "sessions"
        constraints = [
            # Application enforces whether user or counselor column is used for a session.
        ]
