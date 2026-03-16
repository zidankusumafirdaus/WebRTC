from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from apps.schemas.auth_schemas import (
    LoginResponseSchema,
    RegisterResponseSchema,
    LogoutResponseSchema,
)
from apps.service.auth_service import (
    verify_credentials,
    is_username_available,
    create_user,
    create_counselor,
)


def login_controller():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username dan password wajib diisi."}), 400
    try:
        user = verify_credentials(username, password)
        if not user:
            return jsonify({"error": "Username atau password salah."}), 401
        access_token = create_access_token(
            identity=str(user["id"]), additional_claims={"role": user["role"]}
        )
        payload = {
            "access_token": access_token,
            "user_id": str(user["id"]),
            "role": user["role"],
            "display_name": user["display_name"],
        }
        return jsonify(LoginResponseSchema().dump(payload))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def register_user_controller():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    display_name = data.get("display_name")
    if not username or not password or not display_name:
        return (
            jsonify({"error": "Username, password, dan display_name wajib diisi."}),
            400,
        )
    if username != username.lower():
        return jsonify({"error": "Username tidak boleh mengandung huruf kapital."}), 400
    try:
        if not is_username_available(username):
            return jsonify({"error": "Username sudah digunakan."}), 400
        hashed = generate_password_hash(password)
        user_id = create_user(
            username=username, hashed_password=hashed, display_name=display_name
        )
        payload = {"message": "User berhasil didaftarkan.", "user_id": str(user_id)}
        return jsonify(RegisterResponseSchema().dump(payload)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def register_counselor_controller():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    display_name = data.get("display_name")
    bio = data.get("bio")
    qualifications = data.get("qualifications")
    if not username or not password or not display_name:
        return (
            jsonify({"error": "Username, password, dan display_name wajib diisi."}),
            400,
        )
    if username != username.lower():
        return jsonify({"error": "Username tidak boleh mengandung huruf kapital."}), 400
    try:
        if not is_username_available(username):
            return jsonify({"error": "Username sudah digunakan."}), 400
        hashed = generate_password_hash(password)
        counselor_id = create_counselor(
            username=username,
            hashed_password=hashed,
            display_name=display_name,
            bio=bio,
            qualifications=qualifications,
        )
        payload = {
            "message": "Counselor berhasil didaftarkan.",
            "user_id": str(counselor_id),
        }
        return jsonify(RegisterResponseSchema().dump(payload)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def logout_controller():
    payload = {"message": "Logout berhasil."}
    return jsonify(LogoutResponseSchema().dump(payload))
