from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from apps.utils.supabase_client import get_supabase_client
from apps.service.chat.chat_service import get_conversation, is_participant, get_counterparty_id


def _actor_columns(role: str) -> Tuple[str, str]:
    if role == "user":
        return "initiator_user_id", "participant_user_id"
    return "initiator_counselor_id", "participant_counselor_id"


def _counterparty_columns(role: str) -> Tuple[str, str]:
    if role == "user":
        return "initiator_counselor_id", "participant_counselor_id"
    return "initiator_user_id", "participant_user_id"


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def create_call_session(
    conversation_id: int, initiator_id: int, role: str, call_type: str
) -> Dict[str, Any]:
    convo = get_conversation(conversation_id)
    if not convo or not is_participant(convo, initiator_id, role):
        raise PermissionError("forbidden")

    counterparty_id = get_counterparty_id(convo, role)
    now_iso = _now_iso()

    initiator_col, participant_col = _actor_columns(role)
    counterparty_initiator_col, counterparty_participant_col = _counterparty_columns(
        role
    )

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
    }

    supabase = get_supabase_client()
    resp = supabase.table("call_sessions").insert(payload).execute()
    session = resp.data[0]

    participants: List[Dict[str, Any]] = []
    participants.append(
        {
            "call_session_id": session["call_session_id"],
            participant_col: initiator_id,
            counterparty_participant_col: None,
            "role": "caller",
            "status": "calling",
            "joined_at": now_iso,
            "left_at": None,
            "created_at": now_iso,
        }
    )
    if counterparty_id is not None:
        participants.append(
            {
                "call_session_id": session["call_session_id"],
                participant_col: None,
                counterparty_participant_col: counterparty_id,
                "role": "callee",
                "status": "ringing",
                "joined_at": None,
                "left_at": None,
                "created_at": now_iso,
            }
        )

    if participants:
        supabase.table("call_participants").insert(participants).execute()

    return {"call_session": session, "participants": participants}


def list_call_sessions(actor_id: int, role: str, limit: int = 50) -> List[Dict[str, Any]]:
    _, participant_col = _actor_columns(role)
    supabase = get_supabase_client()
    resp = (
        supabase.table("call_participants")
        .select("*")
        .eq(participant_col, actor_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    participant_rows = resp.data or []
    if not participant_rows:
        return []

    call_ids = [row["call_session_id"] for row in participant_rows]
    sessions_resp = (
        supabase.table("call_sessions")
        .select("*")
        .in_("call_session_id", call_ids)
        .execute()
    )
    sessions = {row["call_session_id"]: row for row in (sessions_resp.data or [])}

    items: List[Dict[str, Any]] = []
    for participant in participant_rows:
        session = sessions.get(participant["call_session_id"])
        if session:
            items.append({"call_session": session, "participant": participant})
    return items


def get_call_session(
    call_session_id: int, actor_id: int, role: str
) -> Optional[Dict[str, Any]]:
    _, participant_col = _actor_columns(role)
    supabase = get_supabase_client()
    pr = (
        supabase.table("call_participants")
        .select("call_participant_id")
        .eq("call_session_id", call_session_id)
        .eq(participant_col, actor_id)
        .execute()
    )
    if not pr.data:
        raise PermissionError("forbidden")

    resp = (
        supabase.table("call_sessions")
        .select("*")
        .eq("call_session_id", call_session_id)
        .single()
        .execute()
    )
    return resp.data if resp.data else None


def answer_call(call_session_id: int, actor_id: int, role: str) -> Dict[str, Any]:
    _, participant_col = _actor_columns(role)
    supabase = get_supabase_client()

    pr = (
        supabase.table("call_participants")
        .select("*")
        .eq("call_session_id", call_session_id)
        .eq(participant_col, actor_id)
        .single()
        .execute()
    )
    if not pr.data:
        raise PermissionError("forbidden")

    now_iso = _now_iso()
    supabase.table("call_sessions").update(
        {"status": "active", "started_at": now_iso}
    ).eq("call_session_id", call_session_id).execute()

    participant_payload = {"status": "active"}
    if not pr.data.get("joined_at"):
        participant_payload["joined_at"] = now_iso

    supabase.table("call_participants").update(participant_payload).eq(
        "call_participant_id", pr.data["call_participant_id"]
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
    _, participant_col = _actor_columns(role)
    supabase = get_supabase_client()

    pr = (
        supabase.table("call_participants")
        .select("call_participant_id")
        .eq("call_session_id", call_session_id)
        .eq(participant_col, actor_id)
        .single()
        .execute()
    )
    if not pr.data:
        raise PermissionError("forbidden")

    now_iso = _now_iso()
    supabase.table("call_sessions").update(
        {"status": "ended", "ended_at": now_iso, "ended_reason": reason}
    ).eq("call_session_id", call_session_id).execute()

    supabase.table("call_participants").update(
        {"status": "left", "left_at": now_iso}
    ).eq("call_session_id", call_session_id).execute()

    updated = (
        supabase.table("call_sessions")
        .select("*")
        .eq("call_session_id", call_session_id)
        .single()
        .execute()
    )
    return updated.data
