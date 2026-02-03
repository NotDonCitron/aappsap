from flask import Blueprint, request, jsonify, Response
from app.utils.decorators import manager_required
from app.services.report_service import report_service
from app.models import Order, Product
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')

@reports_bp.route('/sales', methods=['GET'])
@manager_required
def sales_report():
    """Get sales summary."""
    start = request.args.get('start')
    end = request.args.get('end')
    
    if start:
        start = datetime.fromisoformat(start)
    if end:
        end = datetime.fromisoformat(end)
    
    summary = report_service.get_sales_summary(start, end)
    return jsonify(summary)

@reports_bp.route('/inventory', methods=['GET'])
@manager_required
def inventory_report():
    """Get inventory status."""
    report = report_service.get_inventory_report()
    return jsonify(report)

@reports_bp.route('/top-products', methods=['GET'])
@manager_required
def top_products():
    """Get best selling products."""
    limit = request.args.get('limit', 10, type=int)
    days = request.args.get('days', 30, type=int)
    
    products = report_service.get_top_products(limit, days)
    return jsonify({'products': products})

@reports_bp.route('/export/orders', methods=['GET'])
@manager_required
def export_orders():
    """Export orders to CSV."""
    status = request.args.get('status')
    
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).all()
    csv_data = report_service.export_orders_csv(orders)
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=orders_{datetime.now().date()}.csv'
        }
    )

@reports_bp.route('/export/inventory', methods=['GET'])
@manager_required
def export_inventory():
    """Export inventory to CSV."""
    products = Product.query.all()
    csv_data = report_service.export_inventory_csv(products)
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=inventory_{datetime.now().date()}.csv'
        }
    )
