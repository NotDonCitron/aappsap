import pytest
from app.models import Product, Order, db

def test_create_order(client, auth_headers, sample_product):
    """Test creating an order."""
    resp = client.post('/api/v1/orders',
        headers=auth_headers,
        json={
            'items': [
                {
                    'product_id': sample_product.id,
                    'quantity': 5
                }
            ],
            'shipping_cost': 10.00
        }
    )
    
    assert resp.status_code == 201
    assert 'order_number' in resp.json['order']
    assert resp.json['order']['status'] == 'pending'

def test_create_order_insufficient_stock(client, auth_headers, sample_product):
    """Test creating order with insufficient stock."""
    resp = client.post('/api/v1/orders',
        headers=auth_headers,
        json={
            'items': [
                {
                    'product_id': sample_product.id,
                    'quantity': 9999  # Way more than stock
                }
            ]
        }
    )
    
    assert resp.status_code == 400
    assert 'Insufficient stock' in resp.json['error']

def test_list_orders(client, auth_headers, sample_product):
    """Test listing orders."""
    # Create an order first
    client.post('/api/v1/orders',
        headers=auth_headers,
        json={
            'items': [{'product_id': sample_product.id, 'quantity': 2}]
        }
    )
    
    resp = client.get('/api/v1/orders', headers=auth_headers)
    
    assert resp.status_code == 200
    assert resp.json['pagination']['total'] >= 1

def test_get_order(client, auth_headers, sample_product):
    """Test getting order details."""
    # Create order
    create_resp = client.post('/api/v1/orders',
        headers=auth_headers,
        json={
            'items': [{'product_id': sample_product.id, 'quantity': 3}]
        }
    )
    order_id = create_resp.json['order']['id']
    
    resp = client.get(f'/api/v1/orders/{order_id}', headers=auth_headers)
    
    assert resp.status_code == 200
    assert resp.json['order']['id'] == order_id

def test_cancel_order(client, auth_headers, sample_product):
    """Test cancelling an order."""
    # Create order
    create_resp = client.post('/api/v1/orders',
        headers=auth_headers,
        json={
            'items': [{'product_id': sample_product.id, 'quantity': 3}]
        }
    )
    order_id = create_resp.json['order']['id']
    original_stock = sample_product.available_stock
    
    # Cancel order
    resp = client.post(f'/api/v1/orders/{order_id}/cancel', headers=auth_headers)
    
    assert resp.status_code == 200
    assert resp.json['order']['status'] == 'cancelled'

def test_confirm_order(client, auth_headers, admin_headers, sample_product):
    """Test confirming an order (admin only)."""
    # Create order as customer
    create_resp = client.post('/api/v1/orders',
        headers=auth_headers,
        json={
            'items': [{'product_id': sample_product.id, 'quantity': 3}]
        }
    )
    order_id = create_resp.json['order']['id']
    
    # Confirm as admin
    resp = client.post(f'/api/v1/orders/{order_id}/confirm', headers=admin_headers)
    
    assert resp.status_code == 200
    assert resp.json['order']['status'] == 'confirmed'
