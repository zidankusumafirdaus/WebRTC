from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
from marshmallow import ValidationError
from apps.schemas.counselor_request_schemas import (
    CounselorListSchema,
    RequestCounselorSchema,
    RequestResponseSchema,
    RespondRequestSchema,
    RequestListSchema,
    ReportSchema,
    UserRequestSummarySchema,
)
from apps.service.counselor_request_service import (
    list_counselors,
    create_request,
    list_pending_requests,
    list_user_requests,
    respond_request,
    get_reports_if_accepted,
)


def get_counselors_list():
    try:
        counselors = list_counselors()
        return jsonify(CounselorListSchema(many=True).dump(counselors))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_counselor_request():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    try:
        validated = RequestCounselorSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    counselor_id = int(validated["counselor_id"])
    message = validated.get("message")
    try:
        request_id = create_request(
            user_id=user_id,
            counselor_id=counselor_id,
            message=message,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        payload = {
            "message": "Request konsultasi berhasil dikirim.",
            "request_id": request_id,
        }
        return jsonify(RequestResponseSchema().dump(payload)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_pending_requests():
    counselor_id = int(get_jwt_identity())
    try:
        items = list_pending_requests(
            counselor_id=counselor_id, now_iso=datetime.utcnow().isoformat()
        )
        return jsonify(RequestListSchema(many=True).dump(items))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_user_counselor_requests():
    user_id = int(get_jwt_identity())
    try:
        items = list_user_requests(user_id=user_id)
        return jsonify(UserRequestSummarySchema(many=True).dump(items))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def respond_to_request():
    counselor_id = int(get_jwt_identity())
    data = request.get_json() or {}
    if "response_message" in data or "message" in data:
        return (
            jsonify(
                {"error": "response_message tidak diperbolehkan untuk endpoint ini."}
            ),
            400,
        )
    try:
        validated = RespondRequestSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    try:
        conversation_id = respond_request(
            counselor_id=counselor_id,
            request_id=int(validated["request_id"]),
            status=validated["status"],
        )
        return (
            jsonify(
                {
                    "message": f"Request {validated['status']}.",
                    "conversation_id": conversation_id,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_user_reports(user_id: int):
    counselor_id = int(get_jwt_identity())
    try:
        reports = get_reports_if_accepted(
            counselor_id=counselor_id, user_id=int(user_id)
        )
        return jsonify(ReportSchema(many=True).dump(reports))
    except PermissionError:
        return (
            jsonify({"error": "Tidak ada request yang diterima untuk melihat report."}),
            403,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
