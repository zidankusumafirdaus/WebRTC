from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from apps.utils.supabase_client import get_supabase_client
from apps.service.chat.chat_service import get_conversation, is_participant, get_counterparty_id
from apps.service.counselor_request_service import enforce_schedule_access


def _actor_columns(role: str) -> Tuple[str, str]:
    if role == "user":
        return "initiator_user_id", "participant_user_id"
    return "initiator_counselor_id", "participant_counselor_id"


def _participant_columns(role: str) -> Tuple[str, str, str, str]:
    if role == "user":
        return (
            "participant_user_id",
            "participant_user_status",
            "participant_user_joined_at",
            "participant_user_left_at",
        )
    return (
        "participant_counselor_id",
        "participant_counselor_status",
        "participant_counselor_joined_at",
        "participant_counselor_left_at",
    )


def _counterparty_participant_columns(role: str) -> Tuple[str, str, str, str]:
    if role == "user":
        return (
            "participant_counselor_id",
            "participant_counselor_status",
            "participant_counselor_joined_at",
            "participant_counselor_left_at",
        )
    return (
        "participant_user_id",
        "participant_user_status",
        "participant_user_joined_at",
        "participant_user_left_at",
    )


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def create_call_session(
    conversation_id: int, initiator_id: int, role: str, call_type: str
) -> Dict[str, Any]:
    convo = get_conversation(conversation_id)
    if not convo or not is_participant(convo, initiator_id, role):
        raise PermissionError("forbidden")
    enforce_schedule_access(conversation_id, role)

    counterparty_id = get_counterparty_id(convo, role)
    now_iso = _now_iso()

    initiator_col, participant_col = _actor_columns(role)
    counterparty_initiator_col, _ = _actor_columns("counselor" if role == "user" else "user")
    participant_col, participant_status_col, participant_joined_col, participant_left_col = (
        _participant_columns(role)
    )
    (
        counterparty_participant_col,
        counterparty_status_col,
        counterparty_joined_col,
        counterparty_left_col,
    ) = _counterparty_participant_columns(role)

    payload = {
        "conversation_id": conversation_id,
        "call_type": call_type,
        "status": "initiated",
        "created_at": now_iso,
        "started_at": None,
        "ended_at": None,
        "ended_reason": None,
        "metadata": None,
        initiator_col: initiator_id,
        counterparty_initiator_col: None,
        participant_col: initiator_id,
        counterparty_participant_col: counterparty_id,
        participant_status_col: "calling",
        counterparty_status_col: "ringing" if counterparty_id is not None else None,
        participant_joined_col: now_iso,
        counterparty_joined_col: None,
        participant_left_col: None,
        counterparty_left_col: None,
    }

    supabase = get_supabase_client()
    resp = supabase.table("call_sessions").insert(payload).execute()
    session = resp.data[0]
    return {"call_session": session}


def list_call_sessions(actor_id: int, role: str, limit: int = 50) -> List[Dict[str, Any]]:
    participant_col, _, _, _ = _participant_columns(role)
    supabase = get_supabase_client()
    resp = (
        supabase.table("call_sessions")
        .select("*")
        .eq(participant_col, actor_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


def get_call_session(
    call_session_id: int, actor_id: int, role: str
) -> Optional[Dict[str, Any]]:
    participant_col, _, _, _ = _participant_columns(role)
    supabase = get_supabase_client()
    resp = (
        supabase.table("call_sessions")
        .select("*")
        .eq("call_session_id", call_session_id)
        .eq(participant_col, actor_id)
        .single()
        .execute()
    )
    if not resp.data:
        raise PermissionError("forbidden")
    return resp.data


def answer_call(call_session_id: int, actor_id: int, role: str) -> Dict[str, Any]:
    participant_col, participant_status_col, participant_joined_col, _ = _participant_columns(role)
    supabase = get_supabase_client()

    session = (
        supabase.table("call_sessions")
        .select("conversation_id")
        .eq("call_session_id", call_session_id)
        .eq(participant_col, actor_id)
        .single()
        .execute()
    )
    if not session.data:
        raise PermissionError("forbidden")

    convo_id = session.data.get("conversation_id") if session and session.data else None
    if convo_id is not None:
        enforce_schedule_access(int(convo_id), role)

    now_iso = _now_iso()
    supabase.table("call_sessions").update(
        {"status": "active", "started_at": now_iso}
    ).eq("call_session_id", call_session_id).execute()

    participant_payload = {participant_status_col: "active"}
    participant_payload[participant_joined_col] = now_iso

    supabase.table("call_sessions").update(participant_payload).eq(
        "call_session_id", call_session_id
    ).execute()

    updated = (
        supabase.table("call_sessions")
        .select("*")
        .eq("call_session_id", call_session_id)
        .single()
        .execute()
    )
    return updated.data


def end_call(
    call_session_id: int, actor_id: int, role: str, reason: Optional[str]
) -> Dict[str, Any]:
    participant_col, _, _, _ = _participant_columns(role)
    supabase = get_supabase_client()

    pr = (
        supabase.table("call_sessions")
        .select("call_session_id")
        .eq("call_session_id", call_session_id)
        .eq(participant_col, actor_id)
        .single()
        .execute()
    )
    if not pr.data:
        raise PermissionError("forbidden")

    now_iso = _now_iso()
    supabase.table("call_sessions").update(
        {
            "status": "ended",
            "ended_at": now_iso,
            "ended_reason": reason,
            "participant_user_status": "left",
            "participant_counselor_status": "left",
            "participant_user_left_at": now_iso,
            "participant_counselor_left_at": now_iso,
        }
    ).eq("call_session_id", call_session_id).execute()

    updated = (
        supabase.table("call_sessions")
        .select("*")
        .eq("call_session_id", call_session_id)
        .single()
        .execute()
    )
    return updated.data
