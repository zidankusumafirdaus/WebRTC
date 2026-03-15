from datetime import datetime
from peewee import IntegerField, DateTimeField, ForeignKeyField

class UserProfileSummary():
    user = ForeignKeyField('User', backref='profile_summary', column_name='user_id', primary_key=True)
    conversation_count = IntegerField(default=0)
    unique_counselors_count = IntegerField(default=0)
    messages_sent_count = IntegerField(default=0)
    reports_received_count = IntegerField(default=0)
    last_active = DateTimeField(null=True)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'user_profile_summaries'
