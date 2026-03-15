from flask import Blueprint
from apps.utils.auth import jwt_required_custom, role_required
from apps.controllers.auth_controller import (
    login_controller, 
    register_user_controller, 
    logout_controller
    )
from apps.controllers.counselor_request_controller import (
    get_counselors_list, 
    create_counselor_request, 
    get_user_counselor_requests
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
from apps.controllers.report_controller import (
    list_user_reports_controller,
    get_user_report_detail_controller,
    download_user_report_attachment_controller,
)
from apps.controllers.profile_controller import (
    get_user_profile_controller,
)


user_bp = Blueprint('user', __name__, url_prefix='')

# Authentication routes
@user_bp.route('/login', methods=['POST'])
def login():
    return login_controller()

@user_bp.route('/register', methods=['POST'])
def register_user():
    return register_user_controller()

@user_bp.route('/logout', methods=['POST'])
@jwt_required_custom
@role_required('user')
def logout():
    return logout_controller()

# Request Counselor routes
@user_bp.route('/counselors', methods=['GET'])
@jwt_required_custom
@role_required('user')
def list_counselors():
    return get_counselors_list()

# Profile routes
@user_bp.route('/profile', methods=['GET'])
@jwt_required_custom
@role_required('user')
def get_profile():
    return get_user_profile_controller()

@user_bp.route('/request-counselor', methods=['POST'])
@jwt_required_custom
@role_required('user')
def request_counselor():
    return create_counselor_request()

@user_bp.route('/my-counselor-requests', methods=['GET'])
@jwt_required_custom
@role_required('user')
def my_counselor_requests():
    return get_user_counselor_requests()

# Report routes
@user_bp.route('/reports', methods=['GET'])
@jwt_required_custom
@role_required('user')
def list_reports():
    return list_user_reports_controller()

@user_bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required_custom
@role_required('user')
def get_report(report_id: int):
    return get_user_report_detail_controller(report_id)

@user_bp.route('/reports/<int:report_id>/attachment', methods=['GET'])
@jwt_required_custom
@role_required('user')
def get_report_attachment(report_id: int):
    return download_user_report_attachment_controller(report_id)

# Conversation and messaging routes
@user_bp.route('/conversations', methods=['GET'])
@jwt_required_custom
@role_required('user')
def list_conversations():
    return list_conversations_controller()

@user_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required_custom
@role_required('user')
def get_messages(conversation_id: int):
    return get_messages_controller(conversation_id)

@user_bp.route('/messages/send', methods=['POST'])
@jwt_required_custom
@role_required('user')
def send_message_route():
    return send_message_controller()

@user_bp.route('/messages/read', methods=['POST'])
@jwt_required_custom
@role_required('user')
def mark_read_route():
    return mark_read_controller()

@user_bp.route('/messages/<int:message_id>', methods=['PATCH'])
@jwt_required_custom
@role_required('user')
def update_message_route(message_id: int):
    return update_message_controller(message_id)

@user_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required_custom
@role_required('user')
def delete_message_route(message_id: int):
    return delete_message_controller(message_id)

@user_bp.route('/messages/send-attachment', methods=['POST'])
@jwt_required_custom
@role_required('user')
def send_attachment_route():
    return send_attachment_controller()

@user_bp.route('/messages/<int:message_id>/attachment', methods=['GET'])
@jwt_required_custom
@role_required('user')
def get_attachment_route(message_id: int):
    return get_attachment_controller(message_id)