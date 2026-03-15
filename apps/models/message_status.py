from datetime import datetime
from peewee import AutoField, DateTimeField, CharField, ForeignKeyField, SQL

class MessageStatus():
    message_status_id = AutoField()
    message = ForeignKeyField('Message', backref='statuses', column_name='message_id')
    recipient_user = ForeignKeyField('User', null=True, backref='message_statuses', column_name='recipient_user_id')
    recipient_counselor = ForeignKeyField('Counselor', null=True, backref='message_statuses', column_name='recipient_counselor_id')
    status = CharField(null=True)  # sent/delivered/read
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'message_status'
        indexes = (
            (('message', 'recipient_user'), True),
            (('message', 'recipient_counselor'), True),
        )
        constraints = [
            SQL("((recipient_user_id IS NOT NULL)::int + (recipient_counselor_id IS NOT NULL)::int) = 1")
        ]