import random
import string
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric
from app import db

class Order(db.Model):
    __tablename__ = 'orders'
    
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    
    # Pricing
    subtotal = db.Column(Numeric(10, 2), default=0)
    tax_amount = db.Column(Numeric(10, 2), default=0)
    shipping_cost = db.Column(Numeric(10, 2), default=0)
    discount_amount = db.Column(Numeric(10, 2), default=0)
    total_amount = db.Column(Numeric(10, 2), default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Relations
    items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number: ORD-XXXXXX"""
        prefix = 'ORD'
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{suffix}"
    
    def calculate_totals(self):
        """Recalculate all totals from items."""
        subtotal = sum(item.subtotal for item in self.items)
        self.subtotal = Decimal(str(subtotal))
        
        # Calculate tax (e.g., 19%)
        tax_rate = Decimal('0.19')
        self.tax_amount = self.subtotal * tax_rate
        
        # Calculate total
        self.total_amount = (
            self.subtotal + 
            self.tax_amount + 
            self.shipping_cost - 
            self.discount_amount
        )
        db.session.commit()
    
    def confirm(self):
        """Confirm order and finalize stock."""
        if self.status != self.STATUS_PENDING:
            raise ValueError(f"Cannot confirm order with status: {self.status}")
        
        for item in self.items:
            item.product.confirm_stock_removal(item.quantity)
        
        self.status = self.STATUS_CONFIRMED
        self.confirmed_at = datetime.utcnow()
        db.session.commit()
    
    def cancel(self):
        """Cancel order and release reserved stock."""
        if self.status in [self.STATUS_DELIVERED, self.STATUS_CANCELLED]:
            raise ValueError(f"Cannot cancel order with status: {self.status}")
        
        # Release reserved stock
        for item in self.items:
            item.product.release_stock(item.quantity)
        
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'shipping_cost': float(self.shipping_cost),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(Numeric(10, 2), nullable=False)
    discount = db.Column(Numeric(10, 2), default=0)
    
    @property
    def subtotal(self):
        """Calculate item subtotal."""
        unit_price = float(self.unit_price)
        quantity = self.quantity
        discount = float(self.discount) if self.discount else 0
        return (unit_price * quantity) - discount
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'discount': float(self.discount) if self.discount else 0,
            'subtotal': self.subtotal
        }
