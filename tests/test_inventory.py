import pytest
from app.models import Product, db

def test_list_products(client, auth_headers, sample_product):
    """Test listing products."""
    resp = client.get('/api/v1/inventory/products', headers=auth_headers)
    
    assert resp.status_code == 200
    assert len(resp.json['products']) == 1
    assert resp.json['products'][0]['sku'] == 'TEST-001'

def test_get_product(client, auth_headers, sample_product):
    """Test getting single product."""
    resp = client.get(f'/api/v1/inventory/products/{sample_product.id}', headers=auth_headers)
    
    assert resp.status_code == 200
    assert resp.json['product']['name'] == 'Test Product'

def test_create_product(client, admin_headers):
    """Test creating product as admin."""
    resp = client.post('/api/v1/inventory/products',
        headers=admin_headers,
        json={
            'sku': 'NEW-001',
            'name': 'New Product',
            'price': 49.99,
            'stock': 50,
            'category': 'Electronics'
        }
    )
    
    assert resp.status_code == 201
    assert resp.json['product']['sku'] == 'NEW-001'

def test_create_product_duplicate_sku(client, admin_headers, sample_product):
    """Test creating product with duplicate SKU."""
    resp = client.post('/api/v1/inventory/products',
        headers=admin_headers,
        json={
            'sku': 'TEST-001',
            'name': 'Duplicate',
            'price': 10.00,
            'stock': 10
        }
    )
    
    assert resp.status_code == 409

def test_update_product(client, admin_headers, sample_product):
    """Test updating product."""
    resp = client.put(f'/api/v1/inventory/products/{sample_product.id}',
        headers=admin_headers,
        json={
            'name': 'Updated Product Name',
            'price': 39.99
        }
    )
    
    assert resp.status_code == 200
    assert resp.json['product']['name'] == 'Updated Product Name'
    assert float(resp.json['product']['price']) == 39.99

def test_adjust_stock(client, admin_headers, sample_product):
    """Test adjusting stock."""
    original_stock = sample_product.stock
    
    resp = client.patch(f'/api/v1/inventory/products/{sample_product.id}/stock',
        headers=admin_headers,
        json={
            'adjustment': 50,
            'reason': 'Restocking'
        }
    )
    
    assert resp.status_code == 200
    assert resp.json['product']['stock'] == original_stock + 50

def test_list_categories(client, auth_headers, sample_product):
    """Test listing categories."""
    resp = client.get('/api/v1/inventory/categories', headers=auth_headers)
    
    assert resp.status_code == 200
    assert 'categories' in resp.json
