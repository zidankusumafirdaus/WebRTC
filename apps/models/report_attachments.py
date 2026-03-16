from datetime import datetime
from peewee import AutoField, CharField, DateTimeField, IntegerField, ForeignKeyField


class ReportAttachment:
    report_attachments_id = AutoField()
    report = ForeignKeyField("Report", backref="attachments", column_name="report_id")
    filename = CharField(null=True)
    file_path = CharField(null=True)
    size = IntegerField(null=True)
    uploaded_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "report_attachments"
