from apps.utils.supabase_client import get_supabase_client
from datetime import datetime, timedelta, timezone


def list_counselors():
    supabase = get_supabase_client()
    resp = (
        supabase.table("counselors")
        .select("counselor_id, display_name, bio, qualifications")
        .execute()
    )
    return resp.data or []


def create_request(
    user_id: int,
    counselor_id: int,
    message: str | None,
    expires_at: datetime,
    scheduled_at: datetime | None,
    duration_minutes: int | None,
) -> int:
    supabase = get_supabase_client()
    # Counselor exists?
    resp_c = (
        supabase.table("counselors")
        .select("counselor_id")
        .eq("counselor_id", counselor_id)
        .execute()
    )
    if not resp_c.data:
        raise LookupError("Counselor tidak ditemukan.")
    now_iso = datetime.utcnow().isoformat()
    existing = (
        supabase.table("conversations")
        .select("conversation_id, request_status, expires_at")
        .eq("user_id", user_id)
        .eq("counselor_id", counselor_id)
        .single()
        .execute()
    )
    if existing.data:
        if (
            existing.data.get("request_status") == "pending"
            and existing.data.get("expires_at")
            and existing.data.get("expires_at") > now_iso
        ):
            raise ValueError("Anda sudah memiliki request pending ke counselor ini.")

    resp_active = (
        supabase.table("conversations")
        .select("conversation_id")
        .eq("user_id", user_id)
        .eq("request_status", "pending")
        .gt("expires_at", now_iso)
        .execute()
    )
    if resp_active.data and len(resp_active.data) >= 3:
        raise ValueError("Maksimal 3 request aktif yang belum direspons.")

    request_payload = {
        "request_status": "pending",
        "requested_at": now_iso,
        "expires_at": expires_at.isoformat(),
        "response_message": message,
        "scheduled_at": scheduled_at.isoformat() if scheduled_at else None,
        "duration_minutes": duration_minutes,
        "responded_at": None,
        "cancelled_at": None,
        "cancelled_by": None,
        "cancel_reason": None,
    }

    if existing.data:
        resp = (
            supabase.table("conversations")
            .update(request_payload)
            .eq("conversation_id", existing.data["conversation_id"])
            .execute()
        )
        return int(resp.data[0]["conversation_id"])

    new_conversation = {
        "user_id": user_id,
        "counselor_id": counselor_id,
        "created_at": now_iso,
        **request_payload,
    }
    resp = supabase.table("conversations").insert(new_conversation).execute()
    return int(resp.data[0]["conversation_id"])


def list_pending_requests(counselor_id: int, now_iso: str):
    supabase = get_supabase_client()
    resp = (
        supabase.table("conversations")
        .select(
            "conversation_id, user_id, response_message, requested_at, expires_at, scheduled_at, duration_minutes"
        )
        .eq("counselor_id", counselor_id)
        .eq("request_status", "pending")
        .gt("expires_at", now_iso)
        .execute()
    )
    requests = resp.data or []
    normalized = []
    for item in requests:
        item = dict(item)
        item["message"] = item.get("response_message")
        item.pop("response_message", None)
        item["conversation_id"] = item.pop("conversation_id")
        normalized.append(item)
    return normalized


def list_user_requests(user_id: int):
    supabase = get_supabase_client()
    resp = (
        supabase.table("conversations")
        .select(
            "conversation_id, counselor_id, request_status, requested_at, expires_at, responded_at, scheduled_at, duration_minutes"
        )
        .eq("user_id", user_id)
        .order("requested_at", desc=True)
        .execute()
    )
    requests = resp.data or []
    counselor_ids = {
        item.get("counselor_id")
        for item in requests
        if item.get("counselor_id") is not None
    }
    counselor_map = {}
    if counselor_ids:
        resp_c = (
            supabase.table("counselors")
            .select("counselor_id, display_name")
            .in_("counselor_id", list(counselor_ids))
            .execute()
        )
        for counselor in resp_c.data or []:
            counselor_map[counselor["counselor_id"]] = counselor.get("display_name")
    enriched = []
    for item in requests:
        enriched.append(
            {
                "conversation_id": item.get("conversation_id"),
                "counselor_id": item.get("counselor_id"),
                "counselor_name": counselor_map.get(item.get("counselor_id")),
                "status": item.get("request_status"),
                "requested_at": item.get("requested_at"),
                "expires_at": item.get("expires_at"),
                "responded_at": item.get("responded_at"),
                "scheduled_at": item.get("scheduled_at"),
                "duration_minutes": item.get("duration_minutes"),
            }
        )
    return enriched


def respond_request(counselor_id: int, conversation_id: int, status: str):
    supabase = get_supabase_client()
    # Check request ownership
    resp_req = (
        supabase.table("conversations")
        .select("conversation_id, user_id, request_status")
        .eq("conversation_id", conversation_id)
        .eq("counselor_id", counselor_id)
        .execute()
    )
    if not resp_req.data:
        raise LookupError("Request tidak ditemukan atau tidak milik Anda.")
    req = resp_req.data[0]
    if req["request_status"] != "pending":
        raise ValueError("Request sudah direspons.")
    supabase.table("conversations").update(
        {"request_status": status, "responded_at": datetime.utcnow().isoformat()}
    ).eq("conversation_id", conversation_id).execute()
    return conversation_id


def cancel_request(
    user_id: int, conversation_id: int, cancel_reason: str | None
) -> None:
    supabase = get_supabase_client()
    resp_req = (
        supabase.table("conversations")
        .select("conversation_id, request_status")
        .eq("conversation_id", conversation_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not resp_req.data:
        raise LookupError("Request tidak ditemukan.")
    req = resp_req.data[0]
    if req.get("request_status") != "pending":
        raise ValueError("Request sudah direspons dan tidak bisa dibatalkan.")

    update_payload = {
        "status": "cancelled",
        "cancelled_at": datetime.utcnow().isoformat(),
        "cancelled_by": "user",
        "cancel_reason": cancel_reason,
    }
    supabase.table("conversations").update(update_payload).eq(
        "conversation_id", conversation_id
    ).execute()


def get_reports_if_accepted(counselor_id: int, user_id: int):
    supabase = get_supabase_client()
    resp_req = (
        supabase.table("conversations")
        .select("conversation_id")
        .eq("user_id", user_id)
        .eq("counselor_id", counselor_id)
        .eq("request_status", "accepted")
        .execute()
    )
    if not resp_req.data:
        raise PermissionError("Not accepted")
    resp = (
        supabase.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .eq("counselor_id", counselor_id)
        .execute()
    )
    return resp.data or []


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    cleaned = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def enforce_schedule_access(conversation_id: int, role: str | None = None) -> None:
    supabase = get_supabase_client()
    resp_req = (
        supabase.table("conversations")
        .select("conversation_id, request_status, scheduled_at, duration_minutes")
        .eq("conversation_id", conversation_id)
        .single()
        .execute()
    )
    req = resp_req.data if resp_req else None
    if not req:
        return

    scheduled_at = _parse_iso_datetime(req.get("scheduled_at"))
    duration_minutes = req.get("duration_minutes")
    if not scheduled_at:
        return

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    if now < scheduled_at:
        raise ValueError("Sesi belum dimulai.")

    no_show_deadline = scheduled_at + timedelta(minutes=15)
    if now > no_show_deadline and req.get("request_status") == "accepted":
        cancel_reason = "no_show_user" if role == "user" else "no_show_counselor"
        supabase.table("conversations").update(
            {
                "request_status": "cancelled",
                "cancelled_at": now.isoformat(),
                "cancelled_by": "system",
                "cancel_reason": cancel_reason,
            }
        ).eq("conversation_id", req.get("conversation_id")).execute()
        if cancel_reason == "no_show_counselor":
            raise ValueError("Sesi dibatalkan karena konselor tidak hadir.")
        raise ValueError("Sesi dibatalkan karena user tidak hadir.")

    if duration_minutes:
        end_time = scheduled_at + timedelta(minutes=int(duration_minutes))
        if now > end_time:
            raise ValueError("Sesi sudah berakhir.")
