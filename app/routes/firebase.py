"""Firebase API Routes.

Endpoints for Firestore, Auth, Storage, and FCM.
"""
from flask import Blueprint, request, jsonify, g, current_app
from functools import wraps
from app.firebase import (
    firestore_add_document, firestore_get_document, firestore_update_document,
    firestore_delete_document, firestore_query, upload_file, delete_file,
    send_push_notification, send_topic_notification, subscribe_to_topic,
    unsubscribe_from_topic, create_user, delete_user, get_user, firebase_auth_required
)

firebase_bp = Blueprint('firebase', __name__, url_prefix='/api/v1/firebase')


def firebase_enabled(f):
    """Decorator to check if Firebase is enabled."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get('FIREBASE_ENABLED'):
            return jsonify({'error': 'Firebase not configured'}), 503
        return f(*args, **kwargs)
    return decorated_function


# ==================== Firestore Routes ====================

@firebase_bp.route('/firestore/<collection>', methods=['POST'])
@firebase_enabled
def firestore_create(collection):
    """Create document in Firestore."""
    data = request.get_json()
    doc_id = data.pop('id', None)
    doc_id = firestore_add_document(collection, data, doc_id)
    return jsonify({'id': doc_id, 'message': 'Document created'}), 201


@firebase_bp.route('/firestore/<collection>/<doc_id>', methods=['GET'])
@firebase_enabled
def firestore_read(collection, doc_id):
    """Read document from Firestore."""
    doc = firestore_get_document(collection, doc_id)
    if doc is None:
        return jsonify({'error': 'Document not found'}), 404
    return jsonify({'id': doc_id, 'data': doc})


@firebase_bp.route('/firestore/<collection>/<doc_id>', methods=['PUT'])
@firebase_enabled
def firestore_update(collection, doc_id):
    """Update document in Firestore."""
    data = request.get_json()
    firestore_update_document(collection, doc_id, data)
    return jsonify({'message': 'Document updated'})


@firebase_bp.route('/firestore/<collection>/<doc_id>', methods=['DELETE'])
@firebase_enabled
def firestore_delete(collection, doc_id):
    """Delete document from Firestore."""
    firestore_delete_document(collection, doc_id)
    return jsonify({'message': 'Document deleted'})


@firebase_bp.route('/firestore/<collection>/query', methods=['POST'])
@firebase_enabled
def firestore_query_route(collection):
    """Query Firestore collection."""
    data = request.get_json() or {}
    filters = data.get('filters', [])
    order_by = data.get('order_by')
    limit = data.get('limit')
    
    results = firestore_query(collection, filters, order_by, limit)
    return jsonify({'results': results, 'count': len(results)})


# ==================== Storage Routes ====================

@firebase_bp.route('/storage/upload', methods=['POST'])
@firebase_enabled
def storage_upload():
    """Upload file to Cloud Storage."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    path = request.form.get('path', 'uploads/')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    destination = f"{path}{file.filename}"
    url = upload_file(file.read(), destination, file.content_type)
    
    return jsonify({'url': url, 'path': destination})


@firebase_bp.route('/storage/delete', methods=['POST'])
@firebase_enabled
def storage_delete():
    """Delete file from Cloud Storage."""
    data = request.get_json()
    path = data.get('path')
    
    if not path:
        return jsonify({'error': 'Path required'}), 400
    
    delete_file(path)
    return jsonify({'message': 'File deleted'})


# ==================== FCM Routes ====================

@firebase_bp.route('/fcm/send', methods=['POST'])
@firebase_enabled
def fcm_send():
    """Send push notification to device."""
    data = request.get_json()
    token = data.get('token')
    title = data.get('title')
    body = data.get('body')
    custom_data = data.get('data')
    
    if not all([token, title, body]):
        return jsonify({'error': 'token, title, body required'}), 400
    
    message_id = send_push_notification(token, title, body, custom_data)
    return jsonify({'message_id': message_id})


@firebase_bp.route('/fcm/topic/send', methods=['POST'])
@firebase_enabled
def fcm_topic_send():
    """Send push notification to topic."""
    data = request.get_json()
    topic = data.get('topic')
    title = data.get('title')
    body = data.get('body')
    custom_data = data.get('data')
    
    if not all([topic, title, body]):
        return jsonify({'error': 'topic, title, body required'}), 400
    
    message_id = send_topic_notification(topic, title, body, custom_data)
    return jsonify({'message_id': message_id})


@firebase_bp.route('/fcm/subscribe', methods=['POST'])
@firebase_enabled
def fcm_subscribe():
    """Subscribe tokens to topic."""
    data = request.get_json()
    tokens = data.get('tokens', [])
    topic = data.get('topic')
    
    if not tokens or not topic:
        return jsonify({'error': 'tokens and topic required'}), 400
    
    result = subscribe_to_topic(tokens, topic)
    return jsonify({
        'success_count': result.success_count,
        'failure_count': result.failure_count
    })


@firebase_bp.route('/fcm/unsubscribe', methods=['POST'])
@firebase_enabled
def fcm_unsubscribe():
    """Unsubscribe tokens from topic."""
    data = request.get_json()
    tokens = data.get('tokens', [])
    topic = data.get('topic')
    
    if not tokens or not topic:
        return jsonify({'error': 'tokens and topic required'}), 400
    
    result = unsubscribe_from_topic(tokens, topic)
    return jsonify({
        'success_count': result.success_count,
        'failure_count': result.failure_count
    })


# ==================== Firebase Auth Routes ====================

@firebase_bp.route('/auth/user', methods=['POST'])
@firebase_enabled
def auth_create_user():
    """Create Firebase user."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    display_name = data.get('display_name')
    
    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400
    
    try:
        user = create_user(email, password, display_name)
        return jsonify({
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@firebase_bp.route('/auth/user/<uid>', methods=['GET'])
@firebase_enabled
def auth_get_user(uid):
    """Get Firebase user."""
    user = get_user(uid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'uid': user.uid,
        'email': user.email,
        'display_name': user.display_name,
        'email_verified': user.email_verified,
        'disabled': user.disabled
    })


@firebase_bp.route('/auth/user/<uid>', methods=['DELETE'])
@firebase_enabled
def auth_delete_user(uid):
    """Delete Firebase user."""
    try:
        delete_user(uid)
        return jsonify({'message': 'User deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Health Check ====================

@firebase_bp.route('/status', methods=['GET'])
def firebase_status():
    """Check Firebase configuration status."""
    return jsonify({
        'enabled': current_app.config.get('FIREBASE_ENABLED', False),
        'features': {
            'firestore': current_app.config.get('FIREBASE_ENABLED', False),
            'auth': current_app.config.get('FIREBASE_ENABLED', False),
            'storage': current_app.config.get('FIREBASE_ENABLED', False),
            'messaging': current_app.config.get('FIREBASE_ENABLED', False)
        }
    })
