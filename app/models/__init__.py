from app import db
from datetime import datetime, timedelta
import bcrypt
import random
import string

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='customer')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()
    
    def is_admin(self):
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    reserved_stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    weight_kg = db.Column(db.Numeric(8, 3), default=0)  # Weight in kilograms
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    @property
    def available_stock(self):
        return self.stock - self.reserved_stock
    
    def reserve_stock(self, quantity):
        if quantity > self.available_stock:
            raise ValueError(f"Insufficient stock. Available: {self.available_stock}")
        self.reserved_stock += quantity
        db.session.commit()
    
    def release_stock(self, quantity):
        self.reserved_stock = max(0, self.reserved_stock - quantity)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'price': float(self.price),
            'stock': self.stock,
            'available_stock': self.available_stock,
            'category': self.category,
            'is_active': self.is_active,
            'weight_kg': float(self.weight_kg) if self.weight_kg else 0
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_order_number():
        return 'ORD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def calculate_totals(self):
        subtotal = sum(item.subtotal for item in self.items)
        self.total_amount = subtotal
        db.session.commit()
    
    def cancel(self):
        if self.status == self.STATUS_CANCELLED:
            raise ValueError("Order already cancelled")
        for item in self.items:
            item.product.release_stock(item.quantity)
        self.status = self.STATUS_CANCELLED
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    @property
    def subtotal(self):
        return float(self.unit_price) * self.quantity
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': self.subtotal
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')


class ShippingRate(db.Model):
    __tablename__ = 'shipping_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # z.B. "Standard", "Express"
    base_cost = db.Column(db.Numeric(10, 2), default=5.00)
    cost_per_kg = db.Column(db.Numeric(8, 4), default=0.50)
    max_weight = db.Column(db.Numeric(8, 2), nullable=True)  # NULL = unbegrenzt
    is_active = db.Column(db.Boolean, default=True)
    
    def calculate_cost(self, weight_kg):
        """Berechne Versandkosten basierend auf Gewicht."""
        if self.max_weight and weight_kg > float(self.max_weight):
            return None  # Zu schwer
        total = float(self.base_cost) + (float(self.cost_per_kg) * weight_kg)
        return round(total, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'base_cost': float(self.base_cost),
            'cost_per_kg': float(self.cost_per_kg),
            'max_weight': float(self.max_weight) if self.max_weight else None,
            'is_active': self.is_active
        }


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 Sterne
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='reviews')
    product = db.relationship('Product', backref='reviews')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_approved': self.is_approved
        }
