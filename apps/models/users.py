from datetime import datetime
from peewee import AutoField, CharField, DateTimeField


class User:
    user_id = AutoField()
    username = CharField(unique=True, null=False)
    password = CharField(null=True)
    role = CharField(default="user", null=False)
    display_name = CharField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "users"
