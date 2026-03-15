from datetime import datetime
from peewee import IntegerField, DateTimeField, ForeignKeyField

class CounselorProfileSummary():
    counselor = ForeignKeyField('Counselor', backref='profile_summary', column_name='counselor_id', primary_key=True)
    conversation_count = IntegerField(default=0)
    unique_users_count = IntegerField(default=0)
    messages_sent_count = IntegerField(default=0)
    reports_created_count = IntegerField(default=0)
    accepted_requests_count = IntegerField(default=0)
    last_active = DateTimeField(null=True)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'counselor_profile_summaries'
