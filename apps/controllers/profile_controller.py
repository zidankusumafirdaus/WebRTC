from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from apps.schemas.profile_schemas import UserProfileSchema, CounselorProfileSchema
from apps.service.profile_service import get_user_profile, get_counselor_profile


def get_user_profile_controller():
    user_id = int(get_jwt_identity())
    try:
        profile = get_user_profile(user_id=user_id)
        return jsonify(UserProfileSchema().dump(profile))
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_counselor_profile_controller():
    counselor_id = int(get_jwt_identity())
    try:
        profile = get_counselor_profile(counselor_id=counselor_id)
        return jsonify(CounselorProfileSchema().dump(profile))
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
