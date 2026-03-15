from datetime import datetime
from peewee import AutoField, CharField, TextField, DateTimeField, ForeignKeyField, BooleanField

class Report():
    report_id = AutoField()
    conversation = ForeignKeyField('Conversation', backref='reports', column_name='conversation_id')
    counselor = ForeignKeyField('Counselor', backref='reports', column_name='counselor_id')
    user = ForeignKeyField('User', backref='reports', column_name='user_id')
    title = CharField(null=True)
    content = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    delivered = BooleanField(default=False)
    delivered_at = DateTimeField(null=True)

    class Meta:
        table_name = 'reports'
        indexes = (
            (('conversation',), False),
            (('counselor',), False),
            (('user',), False),
        )