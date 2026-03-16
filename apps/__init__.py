from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from flask_socketio import SocketIO
from typing import Optional
from redis import Redis


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize JWT
    JWTManager(app)

    # Routers
    from apps.routes.user_routes import user_bp
    from apps.routes.counselor_routes import counselor_bp
    from apps.routes.health_routes import health_bp

    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(counselor_bp, url_prefix="/api/counselor")
    app.register_blueprint(health_bp, url_prefix="/api/health")

    return app


socketio: Optional[SocketIO] = None


def init_socketio(app: Flask) -> SocketIO:
    global socketio
    if socketio is not None:
        return socketio

    message_queue = None
    url = getattr(Config, "REDIS_URL", None)
    if isinstance(url, str) and url.strip().lower().startswith(
        ("redis://", "rediss://")
    ):
        Redis.from_url(url).ping()
        message_queue = url
    socketio = SocketIO(app, cors_allowed_origins="*", message_queue=message_queue)

    from apps.sockets.chat import register_socketio_handlers

    register_socketio_handlers(socketio)

    return socketio
