from typing import Optional
from flask import request, session
from flask_socketio import join_room, leave_room, emit
from flask import current_app as app
import jwt as pyjwt

from apps.service.chat.chat_service import (
    get_conversation,
    is_participant,
    persist_message,
    mark_read,
    fetch_history,
)


def _extract_token() -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    token = request.args.get("token")
    if token:
        return token
    return None


def _decode_jwt(token: str):
    secret = app.config.get("JWT_SECRET_KEY")
    try:
        decoded = pyjwt.decode(token, secret, algorithms=["HS256"])
        return decoded
    except Exception:
        return None


def register_socketio_handlers(socketio):
    def _require_identity():
        identity = session.get("identity")
        role = session.get("role")
        if not identity or not role:
            emit("error", {"error": "unauthorized"})
            return None, None
        return identity, role

    def _get_room_id(data):
        if not isinstance(data, dict):
            return None
        return data.get("room_id") or data.get("call_id") or data.get("conversation_id")

    @socketio.on("connect")
    def on_connect(auth=None):
        token = None
        if isinstance(auth, dict):
            token = auth.get("token")
        if not token:
            token = _extract_token()
        if not token:
            return False  # refuse connection
        decoded = _decode_jwt(token)
        if not decoded:
            return False
        session["identity"] = decoded.get("sub")
        session["role"] = decoded.get("role")
        emit("connected", {"message": "connected"})

    @socketio.on("join_conversation")
    def on_join(data):
        identity, role = _require_identity()
        if not identity:
            return
        conversation_id = (
            data.get("conversation_id") if isinstance(data, dict) else None
        )
        if not conversation_id:
            emit("error", {"error": "conversation_id required"})
            return
        convo = get_conversation(int(conversation_id))
        if not convo or not is_participant(convo, int(identity), role):
            emit("error", {"error": "forbidden"})
            return
        join_room(str(conversation_id))
        emit("joined", {"conversation_id": conversation_id})

    @socketio.on("leave_conversation")
    def on_leave(data):
        conversation_id = (
            data.get("conversation_id") if isinstance(data, dict) else None
        )
        if conversation_id:
            leave_room(str(conversation_id))
            emit("left", {"conversation_id": conversation_id})

    @socketio.on("send_message")
    def on_send_message(data):
        identity, role = _require_identity()
        if not identity:
            return
        identity = int(identity)
        conversation_id = int(data.get("conversation_id"))
        content = data.get("content")
        content_type = data.get("content_type", "text")
        reply_to = data.get("reply_to")
        convo = get_conversation(conversation_id)
        if not convo or not is_participant(convo, identity, role):
            emit("error", {"error": "forbidden"})
            return
        if not content:
            emit("error", {"error": "content required"})
            return
        msg = persist_message(
            conversation_id, identity, role, content, content_type, reply_to
        )
        # Broadcast to room participants
        socketio.emit("new_message", msg, to=str(conversation_id))

    @socketio.on("mark_read")
    def on_mark_read(data):
        identity, role = _require_identity()
        if not identity:
            return
        identity = int(identity)
        message_ids = data.get("message_ids") if isinstance(data, dict) else None
        if not isinstance(message_ids, list) or not message_ids:
            emit("error", {"error": "message_ids must be a non-empty list"})
            return
        updated = mark_read([int(m) for m in message_ids], identity, role)
        emit("read_ack", {"updated": updated})

    @socketio.on("history")
    def on_history(data):
        identity, role = _require_identity()
        if not identity:
            return
        identity = int(identity)
        conversation_id = int(data.get("conversation_id"))
        before_id = data.get("before_id")
        limit = int(data.get("limit", 50))
        convo = get_conversation(conversation_id)
        if not convo or not is_participant(convo, identity, role):
            emit("error", {"error": "forbidden"})
            return
        items = fetch_history(
            conversation_id,
            limit=limit,
            before_id=int(before_id) if before_id else None,
        )
        emit("history_result", {"items": items})

    @socketio.on("join")
    def on_join_room(data):
        identity, role = _require_identity()
        if not identity:
            return
        room_id = _get_room_id(data)
        if not room_id:
            emit("error", {"error": "room_id required"})
            return
        join_room(str(room_id))
        emit("joined", {"room_id": room_id, "identity": identity, "role": role})

    @socketio.on("offer")
    def on_offer(data):
        identity, role = _require_identity()
        if not identity:
            return
        room_id = _get_room_id(data)
        sdp = data.get("sdp") if isinstance(data, dict) else None
        if not room_id or not isinstance(sdp, dict):
            emit("error", {"error": "room_id and sdp required"})
            return
        payload = {"room_id": room_id, "sdp": sdp, "from": identity, "role": role}
        emit("offer", payload, to=str(room_id), include_self=False)

    @socketio.on("answer")
    def on_answer(data):
        identity, role = _require_identity()
        if not identity:
            return
        room_id = _get_room_id(data)
        sdp = data.get("sdp") if isinstance(data, dict) else None
        if not room_id or not isinstance(sdp, dict):
            emit("error", {"error": "room_id and sdp required"})
            return
        payload = {"room_id": room_id, "sdp": sdp, "from": identity, "role": role}
        emit("answer", payload, to=str(room_id), include_self=False)

    @socketio.on("candidate")
    def on_candidate(data):
        identity, role = _require_identity()
        if not identity:
            return
        room_id = _get_room_id(data)
        candidate = data.get("candidate") if isinstance(data, dict) else None
        if not room_id or not isinstance(candidate, dict):
            emit("error", {"error": "room_id and candidate required"})
            return
        payload = {
            "room_id": room_id,
            "candidate": candidate,
            "from": identity,
            "role": role,
        }
        emit("candidate", payload, to=str(room_id), include_self=False)
