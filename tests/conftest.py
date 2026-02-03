import pytest
from app import create_app, db
from app.models import User, Product

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Create user and return auth headers."""
    user = User(email='test@example.com', role='customer')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    resp = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = resp.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def admin_headers(client):
    """Create admin user and return auth headers."""
    user = User(email='admin@example.com', role='admin')
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    
    resp = client.post('/api/v1/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    
    token = resp.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_product(app):
    product = Product(
        sku='TEST-001',
        name='Test Product',
        price=29.99,
        stock=100
    )
    db.session.add(product)
    db.session.commit()
    return product
