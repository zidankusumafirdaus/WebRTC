from typing import Optional, Dict, Any, List
from datetime import datetime
from apps.utils.supabase_client import get_supabase_client


def get_conversation(conversation_id: int) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("conversations")
        .select("conversation_id, user_id, counselor_id")
        .eq("conversation_id", conversation_id)
        .single()
        .execute()
    )
    return resp.data if resp.data else None


def is_participant(conversation: Dict[str, Any], actor_id: int, role: str) -> bool:
    if role == "user":
        return conversation.get("user_id") == actor_id
    if role == "counselor":
        return conversation.get("counselor_id") == actor_id
    return False


def get_counterparty_id(conversation: Dict[str, Any], role: str) -> Optional[int]:
    if role == "user":
        return conversation.get("counselor_id")
    if role == "counselor":
        return conversation.get("user_id")
    return None


def persist_message(
    conversation_id: int,
    sender_id: int,
    role: str,
    content: str,
    content_type: str = "text",
    reply_to: Optional[int] = None,
) -> Dict[str, Any]:
    now_iso = datetime.utcnow().isoformat()
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise ValueError("conversation not found")
    payload = {
        "conversation_id": conversation_id,
        "content": content,
        "content_type": content_type,
        "created_at": now_iso,
        "reply_to": reply_to,
        "deleted": False,
        "status": "sent",
        "status_updated_at": now_iso,
    }
    if role == "user":
        payload["sender_user_id"] = sender_id
        payload["sender_counselor_id"] = None
        payload["recipient_user_id"] = None
        payload["recipient_counselor_id"] = conversation["counselor_id"]
    else:
        payload["sender_user_id"] = None
        payload["sender_counselor_id"] = sender_id
        payload["recipient_user_id"] = conversation["user_id"]
        payload["recipient_counselor_id"] = None

    supabase = get_supabase_client()
    resp = supabase.table("messages").insert(payload).execute()
    return resp.data[0]


def mark_read(message_ids: List[int], reader_id: int, role: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    now_iso = datetime.utcnow().isoformat()
    updated_count = 0
    updated_ids: List[int] = []
    skipped_ids: List[int] = []

    for mid in message_ids:
        if role == "user":
            q = (
                supabase.table("messages")
                .update({"status": "read", "status_updated_at": now_iso})
                .eq("message_id", mid)
                .eq("recipient_user_id", reader_id)
            )
        else:
            q = (
                supabase.table("messages")
                .update({"status": "read", "status_updated_at": now_iso})
                .eq("message_id", mid)
                .eq("recipient_counselor_id", reader_id)
            )
        resp = q.execute()
        if resp.data:
            updated_count += len(resp.data or [])
            updated_ids.append(mid)
        else:
            skipped_ids.append(mid)

    return {
        "updated_count": updated_count,
        "updated_ids": updated_ids,
        "skipped_ids": skipped_ids,
    }


def fetch_history(
    conversation_id: int, limit: int = 50, before_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    q = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
    )
    if before_id is not None:
        q = q.lt("message_id", before_id)
    q = q.limit(limit)
    resp = q.execute()
    items = resp.data or []
    return list(reversed(items))


def list_conversations_for_actor(actor_id: int, role: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    if role == "user":
        resp = (
            supabase.table("conversations")
            .select("conversation_id, user_id, counselor_id, created_at")
            .eq("user_id", actor_id)
            .order("created_at", desc=True)
            .execute()
        )
    else:
        resp = (
            supabase.table("conversations")
            .select("conversation_id, user_id, counselor_id, created_at")
            .eq("counselor_id", actor_id)
            .order("created_at", desc=True)
            .execute()
        )
    conversations = resp.data or []

    user_ids = {c["user_id"] for c in conversations}
    counselor_ids = {c["counselor_id"] for c in conversations}
    user_map: Dict[int, str] = {}
    counselor_map: Dict[int, str] = {}

    if user_ids:
        ru = (
            supabase.table("users")
            .select("user_id, display_name")
            .in_("user_id", list(user_ids))
            .execute()
        )
        for u in ru.data or []:
            user_map[u["user_id"]] = u.get("display_name")
    if counselor_ids:
        rc = (
            supabase.table("counselors")
            .select("counselor_id, display_name")
            .in_("counselor_id", list(counselor_ids))
            .execute()
        )
        for c in rc.data or []:
            counselor_map[c["counselor_id"]] = c.get("display_name")

    enriched: List[Dict[str, Any]] = []
    for c in conversations:
        enriched.append(
            {
                "conversation_id": c["conversation_id"],
                "user_id": c["user_id"],
                "counselor_id": c["counselor_id"],
                "created_at": c.get("created_at"),
                "counterparty_name": (
                    counselor_map.get(c["counselor_id"])
                    if role == "user"
                    else user_map.get(c["user_id"])
                ),
            }
        )
    return enriched


def update_message(
    message_id: int,
    editor_id: int,
    role: str,
    new_content: str,
    new_content_type: str | None = None,
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("messages")
        .select("*")
        .eq("message_id", message_id)
        .single()
        .execute()
    )
    msg = resp.data
    if not msg:
        raise ValueError("message not found")

    if role == "user" and msg.get("sender_user_id") != editor_id:
        raise PermissionError("not allowed")
    if role == "counselor" and msg.get("sender_counselor_id") != editor_id:
        raise PermissionError("not allowed")

    now_iso = datetime.utcnow().isoformat()
    update_payload = {"content": new_content, "edited_at": now_iso}
    if new_content_type:
        update_payload["content_type"] = new_content_type

    resp2 = (
        supabase.table("messages")
        .update(update_payload)
        .eq("message_id", message_id)
        .execute()
    )
    return resp2.data[0]


def delete_message(
    message_id: int, requester_id: int, role: str, soft: bool = True
) -> None:
    supabase = get_supabase_client()
    resp = (
        supabase.table("messages")
        .select("*")
        .eq("message_id", message_id)
        .single()
        .execute()
    )
    msg = resp.data
    if not msg:
        raise ValueError("message not found")

    if role == "user" and msg.get("sender_user_id") != requester_id:
        raise PermissionError("not allowed")
    if role == "counselor" and msg.get("sender_counselor_id") != requester_id:
        raise PermissionError("not allowed")

    if soft:
        supabase.table("messages").update(
            {"deleted": True, "edited_at": datetime.utcnow().isoformat()}
        ).eq("message_id", message_id).execute()
    else:
        supabase.table("messages").delete().eq("message_id", message_id).execute()
