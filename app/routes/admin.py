from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Product, Order
from app.routes.auth import admin_required
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Search & Filter parameters
    search = request.args.get('search', '').strip()
    role = request.args.get('role')
    is_active = request.args.get('is_active')
    sort_by = request.args.get('sort_by', 'created_at')  # created_at, email, name
    sort_order = request.args.get('sort_order', 'desc')  # asc, desc
    
    query = User.query
    
    # Apply search filter (email or name)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )
    
    # Apply role filter
    if role:
        query = query.filter_by(role=role)
    
    # Apply active status filter
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')
    
    # Apply sorting
    if sort_by == 'name':
        sort_column = User.first_name
    elif sort_by == 'email':
        sort_column = User.email
    else:
        sort_column = User.created_at
    
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        },
        'filters': {
            'search': search,
            'role': role,
            'is_active': is_active
        }
    })

@admin_bp.route('/users/<int:user_id>/role', methods=['PATCH'])
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    new_role = data.get('role')
    if new_role not in ['admin', 'manager', 'customer']:
        return jsonify({'error': 'Invalid role'}), 400
    
    user.role = new_role
    db.session.commit()
    
    return jsonify({'message': 'Role updated', 'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@admin_required
def update_user_status(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    user.is_active = data.get('is_active', user.is_active)
    db.session.commit()
    
    return jsonify({'message': 'Status updated', 'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_detail(user_id):
    """Get detailed user information with orders."""
    user = User.query.get_or_404(user_id)
    
    # Get user's orders
    orders = [o.to_dict() for o in user.orders.order_by(Order.created_at.desc()).limit(10)]
    
    return jsonify({
        'user': user.to_dict(),
        'orders': orders,
        'order_count': user.orders.count()
    })


@admin_bp.route('/products/search', methods=['GET'])
@admin_required
def search_products():
    """Search and filter products."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filter parameters
    search = request.args.get('search', '').strip()
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_stock = request.args.get('min_stock', type=int)
    is_active = request.args.get('is_active')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = Product.query
    
    # Search in name, SKU, description
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    # Category filter
    if category:
        query = query.filter_by(category=category)
    
    # Price range filter
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Stock filter
    if min_stock is not None:
        query = query.filter(Product.stock >= min_stock)
    
    # Active status filter
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')
    
    # Sorting
    sort_columns = {
        'name': Product.name,
        'price': Product.price,
        'stock': Product.stock,
        'created_at': Product.created_at
    }
    sort_column = sort_columns.get(sort_by, Product.name)
    
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'products': [p.to_dict() for p in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        },
        'filters': {
            'search': search,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'min_stock': min_stock
        }
    })


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    stats = {
        'users': {
            'total': User.query.count(),
            'by_role': {
                'admin': User.query.filter_by(role='admin').count(),
                'manager': User.query.filter_by(role='manager').count(),
                'customer': User.query.filter_by(role='customer').count()
            }
        },
        'orders': {
            'total': Order.query.count(),
            'by_status': {
                'pending': Order.query.filter_by(status='pending').count(),
                'confirmed': Order.query.filter_by(status='confirmed').count(),
                'cancelled': Order.query.filter_by(status='cancelled').count()
            }
        },
        'products': {
            'total': Product.query.count(),
            'active': Product.query.filter_by(is_active=True).count()
        },
        'revenue': {
            'total': float(db.session.query(func.sum(Order.total_amount))
                .filter(Order.status != 'cancelled')
                .scalar() or 0)
        }
    }
    
    return jsonify({'stats': stats})
