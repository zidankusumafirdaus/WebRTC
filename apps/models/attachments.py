from datetime import datetime
from peewee import AutoField, CharField, DateTimeField, ForeignKeyField

class Attachment():
    attachments_id = AutoField()
    message = ForeignKeyField('Message', null=True, backref='attachments', column_name='message_id')
    filename = CharField(null=True)
    file_path = CharField(null=True)
    uploaded_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'attachments'