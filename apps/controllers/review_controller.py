from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from apps.schemas.review_schemas import (
    ReviewCreateSchema,
    ReviewCreateByCounselorSchema,
    ReviewItemSchema,
)
from apps.service.review_service import (
    create_review_by_user,
    create_review_by_counselor,
    list_counselor_reviews_for_user,
    get_review_detail_for_user,
    list_reviews_for_counselor,
    get_review_detail_for_counselor,
)


def create_user_review_controller():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    try:
        parsed = ReviewCreateSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    try:
        review = create_review_by_user(
            user_id=user_id,
            target_counselor_id=int(parsed["target_counselor_id"]),
            rating=int(parsed["rating"]),
            comment=parsed.get("comment"),
            session_id=parsed.get("session_id"),
        )
        return jsonify(ReviewItemSchema().dump(review)), 201
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_counselor_review_controller():
    counselor_id = int(get_jwt_identity())
    data = request.get_json() or {}
    try:
        parsed = ReviewCreateByCounselorSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    try:
        review = create_review_by_counselor(
            counselor_id=counselor_id,
            target_user_id=int(parsed["target_user_id"]),
            rating=int(parsed["rating"]),
            comment=parsed.get("comment"),
            session_id=parsed.get("session_id"),
        )
        return jsonify(ReviewItemSchema().dump(review)), 201
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_user_counselor_reviews_controller():
    user_id = int(get_jwt_identity())
    try:
        reviews = list_counselor_reviews_for_user(user_id=user_id)
        return jsonify(ReviewItemSchema(many=True).dump(reviews))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_user_review_detail_controller(review_id: int):
    user_id = int(get_jwt_identity())
    try:
        review = get_review_detail_for_user(user_id=user_id, review_id=review_id)
        if not review:
            return jsonify({"error": "review not found"}), 404
        return jsonify(ReviewItemSchema().dump(review))
    except PermissionError:
        return jsonify({"error": "forbidden"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_counselor_reviews_controller():
    counselor_id = int(get_jwt_identity())
    try:
        reviews = list_reviews_for_counselor(counselor_id=counselor_id)
        return jsonify(ReviewItemSchema(many=True).dump(reviews))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_counselor_review_detail_controller(review_id: int):
    counselor_id = int(get_jwt_identity())
    try:
        review = get_review_detail_for_counselor(
            counselor_id=counselor_id, review_id=review_id
        )
        if not review:
            return jsonify({"error": "review not found"}), 404
        return jsonify(ReviewItemSchema().dump(review))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
