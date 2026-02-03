import pytest
from app.models import User

def test_list_users(client, admin_headers):
    """Test listing users as admin."""
    resp = client.get('/api/v1/admin/users', headers=admin_headers)
    
    assert resp.status_code == 200
    assert 'users' in resp.json

def test_list_users_forbidden(client, auth_headers):
    """Test that regular users cannot list users."""
    resp = client.get('/api/v1/admin/users', headers=auth_headers)
    
    assert resp.status_code == 403

def test_update_user_role(client, admin_headers):
    """Test updating user role."""
    from app import db
    
    # Create a user to update
    user = User(email='roleuser@test.com', role='customer')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    
    resp = client.patch(f'/api/v1/admin/users/{user.id}/role',
        headers=admin_headers,
        json={'role': 'manager'}
    )
    
    assert resp.status_code == 200
    assert resp.json['user']['role'] == 'manager'

def test_update_user_status(client, admin_headers):
    """Test activating/deactivating user."""
    from app import db
    
    # Create a user
    user = User(email='statususer@test.com', role='customer', is_active=True)
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    
    resp = client.patch(f'/api/v1/admin/users/{user.id}/status',
        headers=admin_headers,
        json={'is_active': False}
    )
    
    assert resp.status_code == 200
    assert resp.json['user']['is_active'] == False

def test_get_stats(client, admin_headers):
    """Test getting system statistics."""
    resp = client.get('/api/v1/admin/stats', headers=admin_headers)
    
    assert resp.status_code == 200
    assert 'users' in resp.json['stats']
    assert 'orders' in resp.json['stats']
    assert 'products' in resp.json['stats']
    assert 'total' in resp.json['stats']['users']
    assert 'by_role' in resp.json['stats']['users']
