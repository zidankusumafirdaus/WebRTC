from flask import request, jsonify, send_file
from io import BytesIO
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from apps.schemas.report_schemas import (
    ReportCreateSchema,
    ReportItemSchema,
    ReportCreateResponseSchema,
)
from apps.service.report_service import (
    create_report,
    attach_report_file,
    list_reports_for_user,
    get_report_for_user,
    get_report_attachment,
    download_report_attachment_bytes,
)


def create_report_controller():
    counselor_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    if request.files:
        data = {
            'conversation_id': request.form.get('conversation_id'),
            'title': request.form.get('title'),
            'content': request.form.get('content'),
        }

    try:
        parsed = ReportCreateSchema().load(data)
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400

    try:
        report = create_report(
            counselor_id=counselor_id,
            conversation_id=int(parsed['conversation_id']),
            title=parsed.get('title'),
            content=parsed.get('content'),
        )

        attachment = None
        if request.files:
            file = request.files.get('file')
            if file and file.filename:
                safe_name = secure_filename(file.filename)
                attachment = attach_report_file(report_id=int(report['report_id']), counselor_id=counselor_id, file=file, filename=safe_name)

        payload = ReportCreateResponseSchema().dump({'report': report, 'attachment': attachment})
        return jsonify(payload), 201
    except PermissionError:
        return jsonify({'error': 'forbidden'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def list_user_reports_controller():
    user_id = int(get_jwt_identity())
    try:
        reports = list_reports_for_user(user_id=user_id)
        return jsonify(ReportItemSchema(many=True).dump(reports))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_user_report_detail_controller(report_id: int):
    user_id = int(get_jwt_identity())
    try:
        report = get_report_for_user(report_id=report_id, user_id=user_id)
        if not report:
            return jsonify({'error': 'report not found'}), 404
        return jsonify(ReportItemSchema().dump(report))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def download_user_report_attachment_controller(report_id: int):
    user_id = int(get_jwt_identity())
    try:
        report = get_report_for_user(report_id=report_id, user_id=user_id)
        if not report:
            return jsonify({'error': 'report not found'}), 404

        attachment = get_report_attachment(report_id=report_id)
        if not attachment:
            return jsonify({'error': 'attachment not found'}), 404

        file_path = attachment.get('file_path')
        if not file_path:
            return jsonify({'error': 'file not found'}), 404

        file_bytes = download_report_attachment_bytes(file_path)
        filename = attachment.get('filename') or 'report.pdf'

        return send_file(
            BytesIO(file_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
