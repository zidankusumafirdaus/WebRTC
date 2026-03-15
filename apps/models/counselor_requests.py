from datetime import datetime
from enum import Enum
from peewee import AutoField, DateTimeField, ForeignKeyField, TextField
from playhouse.postgres_ext import EnumField

class RequestStatus(Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'
    expired = 'expired'

class CounselorRequest():
    request_id = AutoField()
    user = ForeignKeyField('User', backref='counselor_requests', column_name='user_id')
    counselor = ForeignKeyField('Counselor', backref='requests', column_name='counselor_id')
    conversation = ForeignKeyField('Conversation', null=True, backref='related_request', column_name='conversation_id')
    status = EnumField(RequestStatus, null=True)
    requested_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(null=True)
    responded_at = DateTimeField(null=True)
    response_message = TextField(null=True)

    class Meta:
        table_name = 'counselor_requests'
        indexes = (
            (('user', 'counselor'), False),
            (('counselor', 'status'), False),
        )