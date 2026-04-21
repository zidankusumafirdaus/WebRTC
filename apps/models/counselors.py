from datetime import datetime
from peewee import AutoField, CharField, TextField, DateTimeField, IntegerField, DecimalField


class Counselor:
    counselor_id = AutoField()
    username = CharField(unique=True, null=False)
    password = CharField(null=True)
    role = CharField(default="counselor", null=False)
    display_name = CharField(null=True)
    bio = TextField(null=True)
    qualifications = TextField(null=True)
    avg_rating = DecimalField(null=True, max_digits=3, decimal_places=2)
    rating_count = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "counselors"
