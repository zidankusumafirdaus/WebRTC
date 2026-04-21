from flask import request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from marshmallow import ValidationError

from apps.schemas.call_schemas import (
    CallStartRequestSchema,
    CallEndRequestSchema,
    CallSessionSchema,
)
from apps.service.call_service import (
    create_call_session,
    list_call_sessions,
    get_call_session,
    answer_call,
    end_call,
)


def start_call_controller():
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    try:
        parsed = CallStartRequestSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    try:
        result = create_call_session(
            conversation_id=int(parsed["conversation_id"]),
            initiator_id=actor_id,
            role=role,
            call_type=parsed.get("call_type", "audio"),
        )
        payload = CallSessionSchema().dump(result["call_session"])
        return jsonify(payload), 201
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_calls_controller():
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    limit = request.args.get("limit", default=50, type=int)

    try:
        items = list_call_sessions(actor_id, role, limit=limit)
        payload = CallSessionSchema(many=True).dump(items)
        return jsonify(payload), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_call_controller(call_session_id: int):
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())

    try:
        session = get_call_session(call_session_id, actor_id, role)
        if not session:
            return jsonify({"error": "not found"}), 404
        payload = CallSessionSchema().dump(session)
        return jsonify(payload), 200
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def answer_call_controller(call_session_id: int):
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())

    try:
        session = answer_call(call_session_id, actor_id, role)
        payload = CallSessionSchema().dump(session)
        return jsonify(payload), 200
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def end_call_controller(call_session_id: int):
    claims = get_jwt()
    role = claims.get("role")
    actor_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    try:
        parsed = CallEndRequestSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    try:
        session = end_call(
            call_session_id,
            actor_id,
            role,
            reason=parsed.get("ended_reason"),
        )
        payload = CallSessionSchema().dump(session)
        return jsonify(payload), 200
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500
