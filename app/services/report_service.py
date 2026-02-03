import csv
import io
from datetime import datetime, timedelta
from sqlalchemy import func
from flask import current_app
from app import db
from app.models import Order, OrderItem, Product

class ReportService:
    """Generate sales and inventory reports."""
    
    def get_sales_summary(self, start_date=None, end_date=None):
        """Get sales summary for date range."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        query = Order.query.filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status != 'cancelled'
        )
        
        total_revenue = query.with_entities(
            func.sum(Order.total_amount)
        ).scalar() or 0
        
        total_orders = query.count()
        
        avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'average_order_value': float(avg_order_value)
        }
    
    def get_inventory_report(self):
        """Get current inventory status."""
        products = Product.query.all()
        
        total_value = sum(
            float(p.price) * p.stock for p in products
        )
        
        low_stock = [p.to_dict() for p in products if p.is_low_stock]
        
        return {
            'total_products': len(products),
            'total_inventory_value': total_value,
            'low_stock_count': len(low_stock),
            'low_stock_items': low_stock
        }
    
    def get_top_products(self, limit=10, days=30):
        """Get top selling products."""
        since = datetime.utcnow() - timedelta(days=days)
        
        results = db.session.query(
            Product.id,
            Product.name,
            Product.sku,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
        ).join(OrderItem).join(Order).filter(
            Order.created_at >= since,
            Order.status != 'cancelled'
        ).group_by(Product.id).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(limit).all()
        
        return [{
            'product_id': r.id,
            'name': r.name,
            'sku': r.sku,
            'total_sold': r.total_sold,
            'revenue': float(r.revenue)
        } for r in results]
    
    def export_orders_csv(self, orders):
        """Export orders to CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Order Number', 'Date', 'Customer', 'Status',
            'Subtotal', 'Tax', 'Shipping', 'Discount', 'Total'
        ])
        
        # Data
        for order in orders:
            writer.writerow([
                order.order_number,
                order.created_at.isoformat(),
                order.user.email,
                order.status,
                float(order.subtotal),
                float(order.tax_amount),
                float(order.shipping_cost),
                float(order.discount_amount),
                float(order.total_amount)
            ])
        
        output.seek(0)
        return output.getvalue()
    
    def export_inventory_csv(self, products):
        """Export inventory to CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'SKU', 'Name', 'Category', 'Price',
            'Stock', 'Reserved', 'Available', 'Value'
        ])
        
        for product in products:
            writer.writerow([
                product.sku,
                product.name,
                product.category or '',
                float(product.price),
                product.stock,
                product.reserved_stock,
                product.available_stock,
                float(product.price) * product.stock
            ])
        
        output.seek(0)
        return output.getvalue()

# Global instance
report_service = ReportService()
