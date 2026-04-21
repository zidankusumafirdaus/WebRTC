from flask import request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from apps.service.chat.chat_service import (
    list_conversations_for_actor,
    get_conversation,
    is_participant,
    fetch_history,
    persist_message,
    mark_read,
    update_message,
    delete_message,
)
from apps.service.counselor_request_service import enforce_schedule_access
from apps.schemas.chat.chat_schemas import (
    ConversationItemSchema,
    MessageSchema,
    SendMessageRequestSchema,
    MarkReadRequestSchema,
    UpdateMessageRequestSchema,
)


def list_conversations_controller():
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    try:
        data = list_conversations_for_actor(actor_id, role)
        payload = ConversationItemSchema(many=True).dump(data)
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_messages_controller(conversation_id: int):
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    before_id = request.args.get("before_id", type=int)
    limit = request.args.get("limit", default=50, type=int)
    try:
        convo = get_conversation(conversation_id)
        if not convo or not is_participant(convo, actor_id, role):
            return jsonify({"error": "forbidden"}), 403
        enforce_schedule_access(conversation_id, role)
        items = fetch_history(conversation_id, limit=limit, before_id=before_id)
        payload = MessageSchema(many=True).dump(items)
        return jsonify(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def send_message_controller():
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    data = request.get_json() or {}
    parsed = SendMessageRequestSchema().load(data)
    conversation_id = int(parsed["conversation_id"])
    content = parsed["content"]
    content_type = parsed.get("content_type", "text")
    reply_to = parsed.get("reply_to")
    try:
        convo = get_conversation(conversation_id)
        if not convo or not is_participant(convo, actor_id, role):
            return jsonify({"error": "forbidden"}), 403
        enforce_schedule_access(conversation_id, role)
        msg = persist_message(
            conversation_id, actor_id, role, content, content_type, reply_to
        )
        payload = MessageSchema().dump(msg)
        return jsonify(payload), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def mark_read_controller():
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    data = request.get_json() or {}
    parsed = MarkReadRequestSchema().load(data)
    message_ids = [int(m) for m in parsed["message_ids"]]
    try:
        result = mark_read(message_ids, actor_id, role)
        updated = int(result.get("updated_count", 0))
        updated_ids = result.get("updated_ids", [])
        skipped_ids = result.get("skipped_ids", [])

        if updated == 0:
            return (
                jsonify(
                    {
                        "updated": 0,
                        "skipped_ids": skipped_ids,
                        "reason": "no matching messages — check that the provided message_ids exist and that you are the recipient",
                    }
                ),
                400,
            )

        if skipped_ids:
            return (
                jsonify(
                    {
                        "updated": updated,
                        "updated_ids": updated_ids,
                        "skipped_ids": skipped_ids,
                        "note": "partial update: some message_ids were not owned by you or already read",
                    }
                ),
                200,
            )

        return jsonify({"updated": updated, "updated_ids": updated_ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_message_controller(message_id: int):
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    data = request.get_json() or {}
    parsed = UpdateMessageRequestSchema().load(data)
    content = parsed["content"]
    content_type = parsed.get("content_type", "text")
    try:
        msg = update_message(message_id, actor_id, role, content, content_type)
        payload = MessageSchema().dump(msg)
        return jsonify(payload), 200
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_message_controller(message_id: int):
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    try:
        delete_message(message_id, actor_id, role, soft=True)
        return "", 204
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
