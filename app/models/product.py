from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric
from app import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    reserved_stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    low_stock_threshold = db.Column(db.Integer, default=10)
    weight_kg = db.Column(Numeric(8, 3), default=0)  # Weight in kilograms
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    @property
    def available_stock(self):
        """Calculate available stock (total - reserved)."""
        return self.stock - self.reserved_stock
    
    @property
    def is_low_stock(self):
        """Check if stock is below threshold."""
        return self.available_stock <= self.low_stock_threshold
    
    def reserve_stock(self, quantity):
        """Atomically reserve stock for an order."""
        if quantity > self.available_stock:
            raise ValueError(f"Insufficient stock. Available: {self.available_stock}")
        
        # Use with_for_update() for race condition protection
        product = Product.query.with_for_update().get(self.id)
        product.reserved_stock += quantity
        db.session.commit()
        return True
    
    def release_stock(self, quantity):
        """Release reserved stock (e.g., on cancel)."""
        self.reserved_stock = max(0, self.reserved_stock - quantity)
        db.session.commit()
    
    def confirm_stock_removal(self, quantity):
        """Convert reserved stock to actual removal (on order completion)."""
        self.stock -= quantity
        self.reserved_stock -= quantity
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'stock': self.stock,
            'available_stock': self.available_stock,
            'reserved_stock': self.reserved_stock,
            'category': self.category,
            'is_active': self.is_active,
            'is_low_stock': self.is_low_stock,
            'weight_kg': float(self.weight_kg) if self.weight_kg else 0
        }
