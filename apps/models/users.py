from datetime import datetime
from peewee import AutoField, CharField, DateTimeField, IntegerField, DecimalField


class User:
    user_id = AutoField()
    username = CharField(unique=True, null=False)
    password = CharField(null=True)
    role = CharField(default="user", null=False)
    display_name = CharField(null=True)
    avg_rating = DecimalField(null=True, max_digits=3, decimal_places=2)
    rating_count = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "users"
