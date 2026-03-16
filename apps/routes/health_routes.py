from flask import Blueprint, jsonify
from redis import Redis
from config import Config

health_bp = Blueprint("health", __name__)


@health_bp.route("/", methods=["GET"])
def health():
    url = getattr(Config, "REDIS_URL", None)
    configured = isinstance(url, str) and url.strip().lower().startswith(
        ("redis://", "rediss://")
    )
    reachable = False
    mode = "inprocess"
    error_message = None
    if configured:
        try:
            Redis.from_url(url).ping()
            reachable = True
            mode = "redis"
        except Exception as e:
            reachable = False
            mode = "inprocess"
            error_message = str(e)
    payload = {
        "redis": {
            "configured": configured,
            "reachable": reachable,
            "mode": mode,
        }
    }
    if configured and not reachable and error_message:
        payload["redis"]["error"] = error_message
    return jsonify(payload)
