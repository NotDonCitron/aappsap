"""Firebase Admin SDK Integration.

Features:
- Firestore database
- Firebase Auth
- Cloud Storage
- Cloud Messaging (FCM)
"""
import os
from functools import wraps
from flask import current_app, g
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage, messaging
from firebase_admin.exceptions import FirebaseError

# Global Firebase app instance
_firebase_app = None
_firestore_client = None
_auth_client = None
_storage_client = None


def init_firebase(app=None):
    """Initialize Firebase Admin SDK."""
    global _firebase_app, _firestore_client, _auth_client, _storage_client
    
    if _firebase_app is not None:
        return _firebase_app
    
    # Path to service account key
    key_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'config',
        'serviceAccountKey.json'
    )
    
    if not os.path.exists(key_path):
        raise FileNotFoundError(
            f"Service account key not found at {key_path}. "
            "Download it from Firebase Console > Project Settings > Service Accounts"
        )
    
    # Initialize Firebase
    cred = credentials.Certificate(key_path)
    _firebase_app = firebase_admin.initialize_app(cred, {
        'storageBucket': f"{cred.project_id}.firebasestorage.app"
    })
    
    # Initialize clients
    _firestore_client = firestore.client()
    _auth_client = auth
    _storage_client = storage.bucket()
    
    print(f"🔥 Firebase initialized: {cred.project_id}")
    return _firebase_app


def get_firestore():
    """Get Firestore client."""
    global _firestore_client
    if _firestore_client is None:
        init_firebase()
    return _firestore_client


def get_auth():
    """Get Firebase Auth client."""
    global _auth_client
    if _auth_client is None:
        init_firebase()
    return _auth_client


def get_storage():
    """Get Cloud Storage bucket."""
    global _storage_client
    if _storage_client is None:
        init_firebase()
    return _storage_client


# ==================== Firestore Helpers ====================

def firestore_add_document(collection, data, doc_id=None):
    """Add document to Firestore."""
    db = get_firestore()
    if doc_id:
        db.collection(collection).document(doc_id).set(data)
        return doc_id
    else:
        doc_ref = db.collection(collection).add(data)
        return doc_ref[1].id


def firestore_get_document(collection, doc_id):
    """Get document from Firestore."""
    db = get_firestore()
    doc = db.collection(collection).document(doc_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


def firestore_update_document(collection, doc_id, data):
    """Update document in Firestore."""
    db = get_firestore()
    db.collection(collection).document(doc_id).update(data)


def firestore_delete_document(collection, doc_id):
    """Delete document from Firestore."""
    db = get_firestore()
    db.collection(collection).document(doc_id).delete()


def firestore_query(collection, filters=None, order_by=None, limit=None):
    """Query Firestore collection.
    
    Args:
        collection: Collection name
        filters: List of tuples (field, operator, value)
        order_by: Tuple (field, direction) direction='ASCENDING'|'DESCENDING'
        limit: Max results
    """
    db = get_firestore()
    query = db.collection(collection)
    
    if filters:
        for field, op, value in filters:
            query = query.where(field, op, value)
    
    if order_by:
        field, direction = order_by
        query = query.order_by(field, direction=direction)
    
    if limit:
        query = query.limit(limit)
    
    return [doc.to_dict() | {'id': doc.id} for doc in query.stream()]


# ==================== Firebase Auth Helpers ====================

def verify_id_token(id_token):
    """Verify Firebase ID token."""
    try:
        return get_auth().verify_id_token(id_token)
    except Exception as e:
        return None


def get_user(uid):
    """Get Firebase user by UID."""
    try:
        return get_auth().get_user(uid)
    except FirebaseError:
        return None


def create_user(email, password, display_name=None):
    """Create Firebase user."""
    return get_auth().create_user(
        email=email,
        password=password,
        display_name=display_name
    )


def delete_user(uid):
    """Delete Firebase user."""
    get_auth().delete_user(uid)


# ==================== Cloud Storage Helpers ====================

def upload_file(file_data, destination_path, content_type=None):
    """Upload file to Cloud Storage.
    
    Returns:
        Public URL of uploaded file
    """
    bucket = get_storage()
    blob = bucket.blob(destination_path)
    
    if content_type:
        blob.content_type = content_type
    
    if isinstance(file_data, bytes):
        blob.upload_from_string(file_data)
    else:
        blob.upload_from_file(file_data)
    
    # Make public and return URL
    blob.make_public()
    return blob.public_url


def delete_file(file_path):
    """Delete file from Cloud Storage."""
    bucket = get_storage()
    blob = bucket.blob(file_path)
    blob.delete()


# ==================== Cloud Messaging Helpers ====================

def send_push_notification(token, title, body, data=None):
    """Send FCM push notification.
    
    Args:
        token: FCM device token
        title: Notification title
        body: Notification body
        data: Optional dict with custom data
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data or {},
        token=token
    )
    
    return messaging.send(message)


def send_topic_notification(topic, title, body, data=None):
    """Send FCM notification to topic."""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data or {},
        topic=topic
    )
    
    return messaging.send(message)


def subscribe_to_topic(tokens, topic):
    """Subscribe tokens to topic."""
    return messaging.subscribe_to_topic(tokens, topic)


def unsubscribe_from_topic(tokens, topic):
    """Unsubscribe tokens from topic."""
    return messaging.unsubscribe_from_topic(tokens, topic)


# ==================== Decorators ====================

def firebase_auth_required(f):
    """Decorator to require Firebase auth token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        
        id_token = auth_header.split('Bearer ')[1]
        decoded_token = verify_id_token(id_token)
        
        if not decoded_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        g.firebase_user = decoded_token
        g.firebase_uid = decoded_token.get('uid')
        
        return f(*args, **kwargs)
    return decorated_function
