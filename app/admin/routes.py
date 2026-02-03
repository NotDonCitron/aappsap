"""Admin dashboard routes."""
from flask import Blueprint, render_template, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from app.models import User, Order, Product
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

import os
admin_bp = Blueprint('admin', __name__, url_prefix='/admin',
                     template_folder='templates')


def admin_required(fn):
    """Decorator to require admin role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user or user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/')
@admin_required
def dashboard():
    """Main dashboard page."""
    return render_template('admin/dashboard.html')


@admin_bp.route('/api/stats')
@admin_required
def dashboard_stats():
    """Get dashboard statistics."""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Sales statistics
    sales_today = db.session.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == today,
        Order.status.in_(['confirmed', 'shipped', 'delivered'])
    ).scalar() or 0
    
    sales_week = db.session.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) >= week_ago,
        Order.status.in_(['confirmed', 'shipped', 'delivered'])
    ).scalar() or 0
    
    sales_month = db.session.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) >= month_ago,
        Order.status.in_(['confirmed', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # Order counts
    orders_today = Order.query.filter(func.date(Order.created_at) == today).count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # Product statistics
    low_stock = Product.query.filter(Product.stock < 10).count()
    total_products = Product.query.count()
    
    # User statistics
    new_users_today = User.query.filter(func.date(User.created_at) == today).count()
    total_users = User.query.count()
    
    return jsonify({
        "sales": {
            "today": round(float(sales_today), 2),
            "week": round(float(sales_week), 2),
            "month": round(float(sales_month), 2)
        },
        "orders": {
            "today": orders_today,
            "pending": pending_orders,
            "total": Order.query.count()
        },
        "inventory": {
            "low_stock": low_stock,
            "total": total_products
        },
        "users": {
            "new_today": new_users_today,
            "total": total_users
        }
    })


@admin_bp.route('/api/chart/sales')
@admin_required
def sales_chart_data():
    """Get sales data for charts (last 30 days)."""
    days = 30
    dates = []
    sales = []
    
    for i in range(days - 1, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
        
        day_sales = db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == date,
            Order.status.in_(['confirmed', 'shipped', 'delivered'])
        ).scalar() or 0
        sales.append(round(float(day_sales), 2))
    
    return jsonify({"labels": dates, "data": sales})


@admin_bp.route('/api/chart/orders')
@admin_required
def orders_chart_data():
    """Get order status distribution."""
    status_counts = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()
    
    return jsonify({
        "labels": [s[0] for s in status_counts],
        "data": [s[1] for s in status_counts]
    })


@admin_bp.route('/api/recent-orders')
@admin_required
def recent_orders():
    """Get recent orders for dashboard."""
    orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return jsonify({
        "orders": [{
            "id": o.id,
            "order_number": o.order_number,
            "customer": o.user.email if o.user else "Guest",
            "total": float(o.total_amount),
            "status": o.status,
            "date": o.created_at.isoformat()
        } for o in orders]
    })
