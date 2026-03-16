from apps.utils.supabase_client import get_supabase_client
from datetime import datetime


def list_counselors():
    supabase = get_supabase_client()
    resp = (
        supabase.table("counselors")
        .select("counselor_id, display_name, bio, qualifications")
        .execute()
    )
    return resp.data or []


def create_request(
    user_id: int, counselor_id: int, message: str | None, expires_at: datetime
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
    # Pending request exists?
    resp_req = (
        supabase.table("counselor_requests")
        .select("request_id")
        .eq("user_id", user_id)
        .eq("counselor_id", counselor_id)
        .eq("status", "pending")
        .execute()
    )
    if resp_req.data:
        raise ValueError("Anda sudah memiliki request pending ke counselor ini.")
    new_request = {
        "user_id": user_id,
        "counselor_id": counselor_id,
        "status": "pending",
        "requested_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
        "response_message": message,
    }
    resp = supabase.table("counselor_requests").insert(new_request).execute()
    return int(resp.data[0]["request_id"])


def list_pending_requests(counselor_id: int, now_iso: str):
    supabase = get_supabase_client()
    resp = (
        supabase.table("counselor_requests")
        .select("request_id, user_id, response_message, requested_at, expires_at")
        .eq("counselor_id", counselor_id)
        .eq("status", "pending")
        .gt("expires_at", now_iso)
        .execute()
    )
    requests = resp.data or []
    normalized = []
    for item in requests:
        item = dict(item)
        item["message"] = item.get("response_message")
        item.pop("response_message", None)
        normalized.append(item)
    return normalized


def list_user_requests(user_id: int):
    supabase = get_supabase_client()
    resp = (
        supabase.table("counselor_requests")
        .select(
            "request_id, counselor_id, status, requested_at, expires_at, responded_at"
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
                "request_id": item.get("request_id"),
                "counselor_id": item.get("counselor_id"),
                "counselor_name": counselor_map.get(item.get("counselor_id")),
                "status": item.get("status"),
                "requested_at": item.get("requested_at"),
                "expires_at": item.get("expires_at"),
                "responded_at": item.get("responded_at"),
            }
        )
    return enriched


def respond_request(counselor_id: int, request_id: int, status: str):
    supabase = get_supabase_client()
    # Check request ownership
    resp_req = (
        supabase.table("counselor_requests")
        .select("request_id, user_id, status")
        .eq("request_id", request_id)
        .eq("counselor_id", counselor_id)
        .execute()
    )
    if not resp_req.data:
        raise LookupError("Request tidak ditemukan atau tidak milik Anda.")
    req = resp_req.data[0]
    if req["status"] != "pending":
        raise ValueError("Request sudah direspons.")
    supabase.table("counselor_requests").update(
        {"status": status, "responded_at": datetime.utcnow().isoformat()}
    ).eq("request_id", request_id).execute()
    conversation_id = None
    if status == "accepted":
        conversation_data = {
            "user_id": req["user_id"],
            "counselor_id": counselor_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        existing = (
            supabase.table("conversations")
            .select("conversation_id")
            .eq("user_id", req["user_id"])
            .eq("counselor_id", counselor_id)
            .execute()
        )
        if existing.data:
            conversation_id = existing.data[0].get("conversation_id")
        else:
            conv_resp = (
                supabase.table("conversations").insert(conversation_data).execute()
            )
            if conv_resp.data:
                conversation_id = conv_resp.data[0].get("conversation_id")
    return conversation_id


def get_reports_if_accepted(counselor_id: int, user_id: int):
    supabase = get_supabase_client()
    resp_req = (
        supabase.table("counselor_requests")
        .select("request_id")
        .eq("user_id", user_id)
        .eq("counselor_id", counselor_id)
        .eq("status", "accepted")
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
