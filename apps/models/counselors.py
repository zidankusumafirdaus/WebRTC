from datetime import datetime
from peewee import AutoField, CharField, TextField, DateTimeField


class Counselor:
    counselor_id = AutoField()
    username = CharField(unique=True, null=False)
    password = CharField(null=True)
    role = CharField(default="counselor", null=False)
    display_name = CharField(null=True)
    bio = TextField(null=True)
    qualifications = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "counselors"
