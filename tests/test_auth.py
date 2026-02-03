import pytest

def test_register(client):
    """Test user registration."""
    resp = client.post('/api/v1/auth/register', json={
        'email': 'new@example.com',
        'password': 'password123',
        'first_name': 'New',
        'last_name': 'User'
    })
    assert resp.status_code == 201
    assert resp.json['user']['email'] == 'new@example.com'

def test_register_duplicate_email(client, auth_headers):
    """Test registration with existing email."""
    resp = client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert resp.status_code == 409

def test_login_success(client, auth_headers):
    """Test successful login."""
    resp = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert resp.status_code == 200
    assert 'access_token' in resp.json
    assert 'refresh_token' in resp.json

def test_login_wrong_password(client):
    """Test login with wrong password."""
    user = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    client.post('/api/v1/auth/register', json=user)
    
    resp = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert resp.status_code == 401

def test_get_current_user(client, auth_headers):
    """Test getting current user."""
    resp = client.get('/api/v1/auth/me', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json['user']['email'] == 'test@example.com'

def test_logout(client, auth_headers):
    """Test logout."""
    resp = client.post('/api/v1/auth/logout', headers=auth_headers)
    assert resp.status_code == 200
