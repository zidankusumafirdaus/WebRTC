from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def jwt_required_custom(fn=None, *, fresh=False, optional=False, refresh=False, locations=None):
    def decorator(inner_fn):
        @wraps(inner_fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(fresh=fresh, optional=optional, refresh=refresh, locations=locations)
            except Exception as e:
                return jsonify({"error": "Unauthorized", "message": str(e)}), 401
            return inner_fn(*args, **kwargs)
        return wrapper
    if fn:
        return decorator(fn)
    return decorator

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                 return jsonify({"success": False, "message": "Token tidak valid atau telah kedaluwarsa.", "error": str(e)}), 401
            
            claims = get_jwt()
            user_role = claims.get('role')

            if not user_role:
                return jsonify({'success': False, 'message': 'Klaim "role" tidak ditemukan di dalam token.'}), 403
            
            if user_role in roles:
                return f(*args, **kwargs)
            
            return jsonify({'success': False, 'message': f'Akses ditolak. Role yang dibutuhkan: {roles}.'}), 403
        return decorated_function
    return decorator
    