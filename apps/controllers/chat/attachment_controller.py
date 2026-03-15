from flask import request, jsonify, send_file
from io import BytesIO
from flask_jwt_extended import get_jwt, get_jwt_identity
from apps.service.chat.chat_service import (
    get_conversation,
    is_participant,
)
from apps.schemas.chat.chat_schemas import MessageSchema
from apps.schemas.chat.attachment_schemas import SendAttachmentResponseSchema
from apps.service.chat.attachment_service import (
    upload_and_create_attachment,
    fetch_attachment_for_message,
    download_attachment_bytes,
    guess_mime_type,
)
from apps import socketio
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import mimetypes

def _detect_file_kind(file: FileStorage) -> str:
    ctype = file.mimetype or mimetypes.guess_type(file.filename or '')[0] or ''
    if ctype.startswith('image/'):
        return 'image'
    if ctype.startswith('video/'):
        return 'video'
    return 'file'

def send_attachment_controller():
    claims = get_jwt()
    role = claims.get('role')
    actor_id = int(get_jwt_identity())
    try:
        conversation_id = request.form.get('conversation_id', type=int)
        if not conversation_id:
            return jsonify({'error': 'conversation_id required'}), 400

        reply_to = request.form.get('reply_to', type=int)
        file: FileStorage = request.files.get('file')
        if not file or not file.filename:
            return jsonify({'error': 'file required'}), 400

        # Validate participation
        convo = get_conversation(conversation_id)
        if not convo or not is_participant(convo, actor_id, role):
            return jsonify({'error': 'forbidden'}), 403

        safe_name = secure_filename(file.filename)
        file_kind = request.form.get('file_kind') or _detect_file_kind(file)

        result = upload_and_create_attachment(
            conversation_id=conversation_id,
            sender_id=actor_id,
            role=role,
            file=file,
            file_kind=file_kind,
            filename=safe_name,
            reply_to=reply_to,
        )

        if socketio and isinstance(result, dict) and 'message' in result:
            socketio.emit('new_message', result['message'], to=str(conversation_id))

        if isinstance(result, dict) and 'message' in result and 'attachment' in result:
            payload = SendAttachmentResponseSchema().dump(result)
        else:
            payload = MessageSchema().dump(result['message']) if isinstance(result, dict) else result
        return jsonify(payload), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_attachment_controller(message_id: int):
    claims = get_jwt()
    role = claims.get('role')
    actor_id = int(get_jwt_identity())
    try:
        record = fetch_attachment_for_message(message_id)
        if not record:
            return jsonify({'error': 'attachment not found'}), 404

        convo = get_conversation(int(record['conversation_id']))
        if not convo or not is_participant(convo, actor_id, role):
            return jsonify({'error': 'forbidden'}), 403

        file_path = record.get('file_path')
        if not file_path:
            return jsonify({'error': 'file not found'}), 404

        file_bytes = download_attachment_bytes(file_path)
        filename = record.get('filename') or 'attachment'
        mime = guess_mime_type(filename)

        content_type = record.get('content_type') or ''
        is_inline = content_type in {'image', 'video'}

        return send_file(
            BytesIO(file_bytes),
            mimetype=mime,
            as_attachment=not is_inline,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500