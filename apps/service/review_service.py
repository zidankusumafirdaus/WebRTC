from datetime import datetime
from typing import Any, Dict, Optional, List

from apps.utils.supabase_client import get_supabase_client


def create_review_by_user(
    user_id: int,
    target_counselor_id: int,
    rating: int,
    comment: Optional[str],
    session_id: Optional[int],
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    convo_resp = (
        supabase.table("conversations")
        .select("conversation_id")
        .eq("user_id", user_id)
        .eq("counselor_id", target_counselor_id)
        .limit(1)
        .execute()
    )
    if not convo_resp.data:
        raise PermissionError("forbidden")

    now_iso = datetime.utcnow().isoformat()
    payload = {
        "session_id": session_id,
        "reviewer_user_id": user_id,
        "reviewer_counselor_id": None,
        "target_user_id": None,
        "target_counselor_id": target_counselor_id,
        "rating": rating,
        "comment": comment,
        "created_at": now_iso,
    }
    resp = supabase.table("reviews").insert(payload).execute()
    return resp.data[0]


def create_review_by_counselor(
    counselor_id: int,
    target_user_id: int,
    rating: int,
    comment: Optional[str],
    session_id: Optional[int],
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    convo_resp = (
        supabase.table("conversations")
        .select("conversation_id")
        .eq("counselor_id", counselor_id)
        .eq("user_id", target_user_id)
        .limit(1)
        .execute()
    )
    if not convo_resp.data:
        raise PermissionError("forbidden")

    now_iso = datetime.utcnow().isoformat()
    payload = {
        "session_id": session_id,
        "reviewer_user_id": None,
        "reviewer_counselor_id": counselor_id,
        "target_user_id": target_user_id,
        "target_counselor_id": None,
        "rating": rating,
        "comment": comment,
        "created_at": now_iso,
    }
    resp = supabase.table("reviews").insert(payload).execute()
    return resp.data[0]


def list_counselor_reviews_for_user(user_id: int) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    convo_resp = (
        supabase.table("conversations")
        .select("counselor_id")
        .eq("user_id", user_id)
        .execute()
    )
    counselor_ids = {
        row.get("counselor_id") for row in (convo_resp.data or []) if row.get("counselor_id")
    }
    if not counselor_ids:
        return []

    resp = (
        supabase.table("reviews")
        .select("*")
        .in_("target_counselor_id", list(counselor_ids))
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


def get_review_detail_for_user(user_id: int, review_id: int) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    review_resp = (
        supabase.table("reviews")
        .select("*")
        .eq("review_id", review_id)
        .single()
        .execute()
    )
    review = review_resp.data if review_resp else None
    if not review:
        return None

    target_counselor_id = review.get("target_counselor_id")
    if not target_counselor_id:
        return None

    allowed = (
        supabase.table("conversations")
        .select("conversation_id")
        .eq("user_id", user_id)
        .eq("counselor_id", target_counselor_id)
        .limit(1)
        .execute()
    )
    if not allowed.data:
        raise PermissionError("forbidden")

    return review


def list_reviews_for_counselor(counselor_id: int) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("reviews")
        .select("*")
        .eq("target_counselor_id", counselor_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


def get_review_detail_for_counselor(
    counselor_id: int, review_id: int
) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("reviews")
        .select("*")
        .eq("review_id", review_id)
        .eq("target_counselor_id", counselor_id)
        .single()
        .execute()
    )
    return resp.data if resp else None
