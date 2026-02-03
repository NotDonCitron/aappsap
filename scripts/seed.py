#!/usr/bin/env python
"""
Database seeding script for testing.
Run: python scripts/seed.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Product

app = create_app('development')

def seed_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Create admin user
        admin = User.query.filter_by(email='admin@shop.com').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                email='admin@shop.com',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create customer user
        customer = User.query.filter_by(email='customer@shop.com').first()
        if not customer:
            print("Creating customer user...")
            customer = User(
                email='customer@shop.com',
                first_name='John',
                last_name='Doe',
                role='customer'
            )
            customer.set_password('customer123')
            db.session.add(customer)
        
        # Create sample products
        products_data = [
            {'sku': 'PHONE-001', 'name': 'Smartphone X', 'price': 699.99, 'stock': 50, 'category': 'Electronics'},
            {'sku': 'LAPTOP-001', 'name': 'Laptop Pro', 'price': 1299.99, 'stock': 30, 'category': 'Electronics'},
            {'sku': 'HEADPHONES-001', 'name': 'Wireless Headphones', 'price': 199.99, 'stock': 100, 'category': 'Electronics'},
            {'sku': 'BOOK-001', 'name': 'Python Programming', 'price': 49.99, 'stock': 200, 'category': 'Books'},
            {'sku': 'SHIRT-001', 'name': 'Cotton T-Shirt', 'price': 29.99, 'stock': 500, 'category': 'Clothing'},
        ]
        
        for data in products_data:
            if not Product.query.filter_by(sku=data['sku']).first():
                print(f"Creating product: {data['name']}")
                product = Product(**data)
                db.session.add(product)
        
        db.session.commit()
        print("✅ Database seeded successfully!")
        print("\nLogin credentials:")
        print("  Admin: admin@shop.com / admin123")
        print("  Customer: customer@shop.com / customer123")

if __name__ == '__main__':
    seed_database()
