from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Order, OrderItem, Product
from app.routes.auth import admin_required

orders_bp = Blueprint('orders', __name__, url_prefix='/api/v1/orders')

@orders_bp.route('', methods=['GET'])
@jwt_required()
def list_orders():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    if claims.get('role') == 'admin':
        query = Order.query
    else:
        query = Order.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'orders': [o.to_dict() for o in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total
        }
    })

@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    items_data = data.get('items', [])
    if not items_data:
        return jsonify({'error': 'Order must contain items'}), 400
    
    # Validate and reserve stock
    order_items = []
    for item in items_data:
        product = Product.query.get(item.get('product_id'))
        if not product:
            return jsonify({'error': f"Product {item.get('product_id')} not found"}), 404
        
        quantity = item.get('quantity', 0)
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        if quantity > product.available_stock:
            return jsonify({
                'error': f'Insufficient stock for {product.name}',
                'available': product.available_stock
            }), 400
        
        order_items.append({'product': product, 'quantity': quantity})
    
    # Create order
    order = Order(
        order_number=Order.generate_order_number(),
        user_id=user_id
    )
    db.session.add(order)
    db.session.flush()
    
    # Create items and reserve stock
    for item_data in order_items:
        product = item_data['product']
        quantity = item_data['quantity']
        
        product.reserve_stock(quantity)
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price
        )
        db.session.add(order_item)
    
    order.calculate_totals()
    db.session.commit()
    
    return jsonify({
        'message': 'Order created',
        'order': order.to_dict()
    }), 201

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    order = Order.query.get_or_404(order_id)
    
    if claims.get('role') != 'admin' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'order': order.to_dict()})

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    order = Order.query.get_or_404(order_id)
    
    if claims.get('role') != 'admin' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        order.cancel()
        return jsonify({
            'message': 'Order cancelled',
            'order': order.to_dict()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@orders_bp.route('/<int:order_id>/confirm', methods=['POST'])
@admin_required
def confirm_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status != Order.STATUS_PENDING:
        return jsonify({'error': f'Cannot confirm order with status: {order.status}'}), 400
    
    order.status = Order.STATUS_CONFIRMED
    db.session.commit()
    
    return jsonify({
        'message': 'Order confirmed',
        'order': order.to_dict()
    })
