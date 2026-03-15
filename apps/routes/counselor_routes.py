from flask import Blueprint
from apps.utils.auth import jwt_required_custom, role_required
from apps.controllers.auth_controller import  (
    login_controller, 
    register_counselor_controller, 
    logout_controller
)
from apps.controllers.counselor_request_controller import (
    get_pending_requests, 
    respond_to_request, 
    get_user_reports
)
from apps.controllers.report_controller import (
    create_report_controller,
)
from apps.controllers.chat.chat_controller import (
    list_conversations_controller,
    get_messages_controller,
    send_message_controller,
    mark_read_controller,
    update_message_controller,
    delete_message_controller,
)
from apps.controllers.chat.attachment_controller import (
    send_attachment_controller,
    get_attachment_controller,
)
from apps.controllers.profile_controller import (
    get_counselor_profile_controller,
)

counselor_bp = Blueprint('counselor', __name__)

# Authentication routes
@counselor_bp.route('/login', methods=['POST'])
def login():
    return login_controller()

@counselor_bp.route('/register', methods=['POST'])
def register_counselor():
    return register_counselor_controller()

@counselor_bp.route('/logout', methods=['POST'])
@jwt_required_custom
@role_required('counselor')
def logout():
    return logout_controller()

# Request management routes
@counselor_bp.route('/requests', methods=['GET'])
@jwt_required_custom
@role_required('counselor')
def get_requests():
    return get_pending_requests()

# Profile routes
@counselor_bp.route('/profile', methods=['GET'])
@jwt_required_custom
@role_required('counselor')
def get_profile():
    return get_counselor_profile_controller()

@counselor_bp.route('/respond-request', methods=['POST'])
@jwt_required_custom
@role_required('counselor')
def respond_request():
    return respond_to_request()

@counselor_bp.route('/user-reports/<int:user_id>', methods=['GET'])
@jwt_required_custom
@role_required('counselor')
def get_reports(user_id):
    return get_user_reports(user_id)

@counselor_bp.route('/reports', methods=['POST'])
@jwt_required_custom
@role_required('counselor')
def create_report():
    return create_report_controller()

# Conversation and messaging routes
@counselor_bp.route('/conversations', methods=['GET'])
@jwt_required_custom
@role_required('counselor')
def list_conversations():
    return list_conversations_controller()

@counselor_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required_custom
@role_required('counselor')
def get_messages(conversation_id: int):
    return get_messages_controller(conversation_id)

@counselor_bp.route('/messages/send', methods=['POST'])
@jwt_required_custom
@role_required('counselor')
def send_message_route():
    return send_message_controller()

@counselor_bp.route('/messages/read', methods=['POST'])
@jwt_required_custom
@role_required('counselor')
def mark_read_route():
    return mark_read_controller()

@counselor_bp.route('/messages/<int:message_id>', methods=['PATCH'])
@jwt_required_custom
@role_required('counselor')
def update_message_route(message_id: int):
    return update_message_controller(message_id)

@counselor_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required_custom
@role_required('counselor')
def delete_message_route(message_id: int):
    return delete_message_controller(message_id)

@counselor_bp.route('/messages/send-attachment', methods=['POST'])
@jwt_required_custom
@role_required('counselor')
def send_attachment_route():
    return send_attachment_controller()

@counselor_bp.route('/messages/<int:message_id>/attachment', methods=['GET'])
@jwt_required_custom
@role_required('counselor')
def get_attachment_route(message_id: int):
    return get_attachment_controller(message_id)