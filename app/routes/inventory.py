from flask import Blueprint, request, jsonify
from app import db
from app.models import Product
from app.routes.auth import jwt_required, manager_required

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/v1/inventory')

@inventory_bp.route('/products', methods=['GET'])
@jwt_required()
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    
    query = Product.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(Product.name).paginate(
        page=page, per_page=min(per_page, 100), error_out=False
    )
    
    return jsonify({
        'products': [p.to_dict() for p in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })

@inventory_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'product': product.to_dict()})

@inventory_bp.route('/products', methods=['POST'])
@manager_required
def create_product():
    data = request.get_json()
    
    required = ['sku', 'name', 'price', 'stock']
    if not all(f in data for f in required):
        return jsonify({'error': f'Missing required: {required}'}), 400
    
    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'SKU already exists'}), 409
    
    product = Product(
        sku=data['sku'],
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        stock=data['stock'],
        category=data.get('category'),
        weight_kg=data.get('weight_kg', 0)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product created',
        'product': product.to_dict()
    }), 201

@inventory_bp.route('/products/<int:product_id>', methods=['PUT'])
@manager_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    updatable = ['name', 'description', 'price', 'stock', 'category', 'is_active', 'weight_kg']
    for field in updatable:
        if field in data:
            setattr(product, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Product updated',
        'product': product.to_dict()
    })

@inventory_bp.route('/categories', methods=['GET'])
@jwt_required()
def list_categories():
    categories = db.session.query(Product.category).distinct().all()
    return jsonify({'categories': [c[0] for c in categories if c[0]]})

@inventory_bp.route('/products/<int:product_id>/stock', methods=['PATCH'])
@manager_required
def adjust_stock(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    adjustment = data.get('adjustment')
    if adjustment is None:
        return jsonify({'error': 'adjustment required'}), 400
    
    new_stock = product.stock + adjustment
    if new_stock < 0:
        return jsonify({'error': 'Insufficient stock for adjustment'}), 400
    
    product.stock = new_stock
    db.session.commit()
    
    return jsonify({
        'message': 'Stock adjusted',
        'product': product.to_dict()
    })
