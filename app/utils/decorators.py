from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt

def role_required(*allowed_roles):
    """Decorator to require specific role(s)."""
    def decorator(fn):
        @jwt_required()
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role', 'customer')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required': list(allowed_roles),
                    'current': user_role
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Convenience decorators
admin_required = role_required('admin')
manager_required = role_required('admin', 'manager')
authenticated = jwt_required()
