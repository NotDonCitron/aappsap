"""Shipping routes for calculating shipping costs."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import ShippingRate, Product
from app.routes.auth import admin_required

shipping_bp = Blueprint('shipping', __name__, url_prefix='/api/v1/shipping')


@shipping_bp.route('/calculate', methods=['POST'])
@jwt_required()
def calculate_shipping():
    """Calculate shipping cost for a list of products."""
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'No items provided'}), 400
    
    # Calculate total weight
    total_weight = 0
    for item in items:
        product = Product.query.get(item.get('product_id'))
        if not product:
            return jsonify({'error': f"Product {item.get('product_id')} not found"}), 404
        quantity = item.get('quantity', 1)
        total_weight += float(product.weight_kg) * quantity
    
    # Get active shipping rates
    rates = ShippingRate.query.filter_by(is_active=True).all()
    
    results = []
    for rate in rates:
        cost = rate.calculate_cost(total_weight)
        if cost is not None:
            results.append({
                'rate': rate.to_dict(),
                'cost': cost,
                'total_weight': round(total_weight, 3)
            })
    
    return jsonify({
        'total_weight_kg': round(total_weight, 3),
        'options': results
    })


@shipping_bp.route('/rates', methods=['GET'])
def list_rates():
    """Get all active shipping rates."""
    rates = ShippingRate.query.filter_by(is_active=True).all()
    return jsonify({'rates': [r.to_dict() for r in rates]})


@shipping_bp.route('/rates', methods=['POST'])
@admin_required
def create_rate():
    """Create a new shipping rate (admin only)."""
    data = request.get_json()
    
    rate = ShippingRate(
        name=data.get('name'),
        base_cost=data.get('base_cost', 5.00),
        cost_per_kg=data.get('cost_per_kg', 0.50),
        max_weight=data.get('max_weight'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(rate)
    db.session.commit()
    
    return jsonify({
        'message': 'Shipping rate created',
        'rate': rate.to_dict()
    }), 201


@shipping_bp.route('/rates/<int:rate_id>', methods=['DELETE'])
@admin_required
def delete_rate(rate_id):
    """Delete a shipping rate (admin only)."""
    rate = ShippingRate.query.get_or_404(rate_id)
    rate.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Shipping rate deactivated'})
