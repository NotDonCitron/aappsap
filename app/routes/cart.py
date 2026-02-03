"""Shopping cart routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Product, CartItem, User

cart_bp = Blueprint('cart', __name__, url_prefix='/api/v1/cart')


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Get user's cart."""
    user_id = int(get_jwt_identity())
    
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    items = []
    total = 0
    for item in cart_items:
        product = item.product
        if product:
            subtotal = float(product.price) * item.quantity
            total += subtotal
            items.append({
                'id': item.id,
                'product': product.to_dict(),
                'quantity': item.quantity,
                'subtotal': subtotal
            })
    
    return jsonify({
        'items': items,
        'total': round(total, 2),
        'item_count': sum(item['quantity'] for item in items)
    })


@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add product to cart."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400
    
    product = Product.query.get_or_404(product_id)
    
    if quantity > product.available_stock:
        return jsonify({
            'error': 'Insufficient stock',
            'available': product.available_stock
        }), 400
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Added to cart',
        'item': {
            'product': product.to_dict(),
            'quantity': cart_item.quantity
        }
    })


@cart_bp.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=user_id
    ).first_or_404()
    
    quantity = data.get('quantity', 0)
    
    if quantity <= 0:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart'})
    
    if quantity > cart_item.product.available_stock:
        return jsonify({
            'error': 'Insufficient stock',
            'available': cart_item.product.available_stock
        }), 400
    
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({
        'message': 'Cart updated',
        'item': {
            'product': cart_item.product.to_dict(),
            'quantity': cart_item.quantity
        }
    })


@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart."""
    user_id = int(get_jwt_identity())
    
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=user_id
    ).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'})


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear entire cart."""
    user_id = int(get_jwt_identity())
    
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Cart cleared'})
