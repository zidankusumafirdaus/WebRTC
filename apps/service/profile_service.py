from typing import Dict, Any
from apps.utils.supabase_client import get_supabase_client


def get_user_profile(user_id: int) -> Dict[str, Any]:
    supabase = get_supabase_client()
    resp_user = (
        supabase.table("users")
        .select("user_id, username, display_name, created_at")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    user = resp_user.data
    if not user:
        raise LookupError("User tidak ditemukan.")

    resp_summary = (
        supabase.table("user_profile_summaries")
        .select("*")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    summary = resp_summary.data or {}
    if not summary:
        summary = {
            "user_id": user_id,
            "conversation_count": 0,
            "unique_counselors_count": 0,
            "messages_sent_count": 0,
            "reports_received_count": 0,
            "last_active": None,
            "updated_at": None,
        }

    merged = {**user, **summary}
    return merged


def get_counselor_profile(counselor_id: int) -> Dict[str, Any]:
    supabase = get_supabase_client()
    resp_counselor = (
        supabase.table("counselors")
        .select("counselor_id, username, display_name, bio, qualifications, created_at")
        .eq("counselor_id", counselor_id)
        .single()
        .execute()
    )
    counselor = resp_counselor.data
    if not counselor:
        raise LookupError("Counselor tidak ditemukan.")

    resp_summary = (
        supabase.table("counselor_profile_summaries")
        .select("*")
        .eq("counselor_id", counselor_id)
        .single()
        .execute()
    )
    summary = resp_summary.data or {}
    if not summary:
        summary = {
            "counselor_id": counselor_id,
            "conversation_count": 0,
            "unique_users_count": 0,
            "messages_sent_count": 0,
            "reports_created_count": 0,
            "accepted_requests_count": 0,
            "last_active": None,
            "updated_at": None,
        }

    merged = {**counselor, **summary}
    return merged
