from __future__ import annotations

from typing import Optional, Dict, Any, List
from datetime import datetime
import io
import mimetypes
import uuid

from apps.utils.supabase_client import get_supabase_client
from apps.service.chat.chat_service import get_conversation, is_participant
from config import Config

PDF_MIME_FALLBACKS = {
    "application/pdf",
    "application/x-pdf",
    "application/acrobat",
    "application/vnd.pdf",
}


def _report_bucket() -> str:
    return getattr(Config, "SUPABASE_REPORTS_BUCKET", None) or getattr(
        Config, "SUPABASE_ATTACHMENTS_BUCKET", "attachments"
    )


def _build_storage_path(report_id: int, filename: str) -> str:
    now = datetime.utcnow()
    unique = uuid.uuid4().hex
    return f"report-{report_id}/{now.year:04d}/{now.month:02d}/{now.day:02d}/{unique}_{filename}"


def _is_pdf_allowed(filename: Optional[str], mimetype: Optional[str]) -> bool:
    allowed_env = getattr(Config, "REPORT_ALLOWED_MIME_FULL", None)
    if isinstance(allowed_env, (set, list, tuple)) and allowed_env:
        allowed = {str(v).strip() for v in allowed_env if str(v).strip()}
    else:
        allowed = set(PDF_MIME_FALLBACKS)

    if mimetype in allowed:
        return True

    name = (filename or "").lower().strip()
    if name.endswith(".pdf"):
        return True

    if not mimetype:
        return False

    guessed = mimetypes.guess_type(filename or "")[0]
    if guessed in allowed:
        return True

    if mimetype == "application/octet-stream" and name.endswith(".pdf"):
        return True

    return False


def create_report(
    counselor_id: int,
    conversation_id: int,
    title: Optional[str],
    content: Optional[str],
) -> Dict[str, Any]:
    convo = get_conversation(conversation_id)
    if not convo or not is_participant(convo, counselor_id, "counselor"):
        raise PermissionError("forbidden")

    now_iso = datetime.utcnow().isoformat()
    payload = {
        "conversation_id": conversation_id,
        "counselor_id": counselor_id,
        "user_id": convo.get("user_id"),
        "title": title,
        "content": content,
        "created_at": now_iso,
        "delivered": True,
        "delivered_at": now_iso,
    }
    supabase = get_supabase_client()
    resp = supabase.table("reports").insert(payload).execute()
    return resp.data[0]


def attach_report_file(
    report_id: int, counselor_id: int, file, filename: str
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    report_resp = (
        supabase.table("reports")
        .select("report_id, counselor_id")
        .eq("report_id", report_id)
        .single()
        .execute()
    )
    report = report_resp.data if report_resp else None
    if not report:
        raise ValueError("report not found")
    if int(report.get("counselor_id")) != int(counselor_id):
        raise PermissionError("forbidden")

    mimetype = getattr(file, "mimetype", None) or None
    file.stream.seek(0, io.SEEK_END)
    size_bytes = file.stream.tell()
    file.stream.seek(0)

    max_bytes = Config.MAX_FILE_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise RuntimeError(
            f"File too large ({size_bytes} bytes). Max is {max_bytes} bytes."
        )

    if not _is_pdf_allowed(filename, mimetype):
        raise RuntimeError("Only PDF files are allowed for reports.")

    storage_path = _build_storage_path(report_id, filename)
    file_bytes = file.stream.read()

    file_options = {
        "content-type": mimetype or "application/pdf",
        "cache-control": "max-age=31536000",
        "upsert": False,
    }

    bucket = _report_bucket()
    try:
        upload_resp = supabase.storage.from_(bucket).upload(
            storage_path, file_bytes, file_options=file_options
        )
    except TypeError as exc:
        raise RuntimeError(f"Upload call failed (type error): {exc}")
    except Exception as exc:
        raise RuntimeError(f"Upload call failed: {exc}")

    error = None
    try:
        if isinstance(upload_resp, dict):
            error = upload_resp.get("error")
        else:
            error = getattr(upload_resp, "error", None)
    except Exception:
        error = None

    if error:
        raise RuntimeError(f"Upload failed: {error}")

    now_iso = datetime.utcnow().isoformat()
    attach_payload = {
        "report_id": report_id,
        "filename": filename,
        "file_path": storage_path,
        "size": size_bytes,
        "uploaded_at": now_iso,
    }
    supabase.table("report_attachments").insert(attach_payload).execute()

    public_url = None
    try:
        public_url = supabase.storage.from_(bucket).get_public_url(storage_path)
    except Exception:
        public_url = None

    return {
        "filename": filename,
        "file_path": storage_path,
        "size": size_bytes,
        "uploaded_at": now_iso,
        "public_url": public_url,
    }


def list_reports_for_user(user_id: int) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


def list_reports_for_counselor_user(
    counselor_id: int, user_id: int
) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .eq("counselor_id", counselor_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


def get_report_for_user(report_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("reports")
        .select("*")
        .eq("report_id", report_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return resp.data if resp else None


def get_report_for_counselor(
    report_id: int, counselor_id: int
) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("reports")
        .select("*")
        .eq("report_id", report_id)
        .eq("counselor_id", counselor_id)
        .single()
        .execute()
    )
    return resp.data if resp else None


def get_report_attachment(report_id: int) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("report_attachments")
        .select("filename, file_path, size, uploaded_at")
        .eq("report_id", report_id)
        .single()
        .execute()
    )
    return resp.data if resp else None


def download_report_attachment_bytes(file_path: str) -> bytes:
    supabase = get_supabase_client()
    bucket = _report_bucket()
    resp = supabase.storage.from_(bucket).download(file_path)

    if hasattr(resp, "content"):
        return resp.content
    if isinstance(resp, (bytes, bytearray)):
        return bytes(resp)
    if isinstance(resp, str):
        return resp.encode("utf-8")
    raise RuntimeError("Unexpected download response type")
