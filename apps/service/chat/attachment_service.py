from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import io
from apps.utils.supabase_client import get_supabase_client
from apps.service.chat.chat_service import persist_message
from config import Config
import mimetypes

def _build_storage_path(conversation_id: int, filename: str) -> str:
    now = datetime.utcnow()
    unique = uuid.uuid4().hex
    return f"conv-{conversation_id}/{now.year:04d}/{now.month:02d}/{now.day:02d}/{unique}_{filename}"

def _is_mime_allowed(mime: str) -> bool:
    if not mime:
        return False
    for p in Config.ALLOWED_MIME_PREFIXES:
        if mime.startswith(p):
            return True
    if mime in Config.ALLOWED_MIME_FULL:
        return True
    return False

def upload_and_create_attachment(
    conversation_id: int,
    sender_id: int,
    role: str,
    file,
    file_kind: str,
    filename: str,
    reply_to: Optional[int] = None,
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    bucket = getattr(Config, 'SUPABASE_ATTACHMENTS_BUCKET', 'attachments')

    mimetype = getattr(file, 'mimetype', None) or None
    file.stream.seek(0, io.SEEK_END)
    size_bytes = file.stream.tell()
    file.stream.seek(0)

    max_bytes = Config.MAX_FILE_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise RuntimeError(f"File too large ({size_bytes} bytes). Max is {max_bytes} bytes.")

    if not _is_mime_allowed(mimetype):
        raise RuntimeError(f"Unsupported media type: {mimetype}")

    storage_path = _build_storage_path(conversation_id, filename)
    file_bytes = file.stream.read()

    file_options = {
        'content-type': mimetype or 'application/octet-stream',
        'cache-control': 'max-age=31536000',
        'upsert': False,
    }
    try:
        upload_resp = supabase.storage.from_(bucket).upload(storage_path, file_bytes, file_options=file_options)
    except TypeError as exc:
        raise RuntimeError(f"Upload call failed (type error): {exc}")
    except Exception as exc:
        raise RuntimeError(f"Upload call failed: {exc}")

    error = None
    try:
        if isinstance(upload_resp, dict):
            error = upload_resp.get('error')
        else:
            error = getattr(upload_resp, 'error', None)
    except Exception:
        error = None

    if error:
        raise RuntimeError(f"Upload failed: {error}")

    try:
        public_url = supabase.storage.from_(bucket).get_public_url(storage_path)
    except Exception:
        public_url = None

    msg = persist_message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        role=role,
        content=str(public_url) if public_url is not None else storage_path,
        content_type=file_kind,
        reply_to=reply_to,
    )

    now_iso = datetime.utcnow().isoformat()
    attach_payload = {
        'message_id': msg['message_id'],
        'filename': filename,
        'file_path': storage_path,
        'uploaded_at': now_iso,
    }
    supabase.table('attachments').insert(attach_payload).execute()

    return {
        'message': msg,
        'attachment': {
            'filename': filename,
            'file_path': storage_path,
            'public_url': public_url,
        },
    }

def fetch_attachment_for_message(message_id: int) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    msg_resp = supabase.table('messages').select('message_id, conversation_id, content_type').eq('message_id', message_id).single().execute()
    msg = msg_resp.data if msg_resp else None
    if not msg:
        return None

    att_resp = supabase.table('attachments').select('filename, file_path, uploaded_at').eq('message_id', message_id).single().execute()
    att = att_resp.data if att_resp else None
    if not att:
        return None

    return {
        'message_id': msg.get('message_id'),
        'conversation_id': msg.get('conversation_id'),
        'content_type': msg.get('content_type'),
        'filename': att.get('filename'),
        'file_path': att.get('file_path'),
        'uploaded_at': att.get('uploaded_at'),
    }

def download_attachment_bytes(file_path: str) -> bytes:
    supabase = get_supabase_client()
    bucket = getattr(Config, 'SUPABASE_ATTACHMENTS_BUCKET', 'attachments')
    resp = supabase.storage.from_(bucket).download(file_path)

    if hasattr(resp, 'content'):
        return resp.content
    if isinstance(resp, (bytes, bytearray)):
        return bytes(resp)
    if isinstance(resp, str):
        return resp.encode('utf-8')
    raise RuntimeError('Unexpected download response type')

def guess_mime_type(filename: Optional[str]) -> str:
    if not filename:
        return 'application/octet-stream'
    guessed = mimetypes.guess_type(filename)[0]
    return guessed or 'application/octet-stream'