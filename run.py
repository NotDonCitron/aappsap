#!/usr/bin/env python
from app import create_app, db
from app.models import User, Product, Order

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Order': Order
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    app.run(host='0.0.0.0', port=5000, debug=True)
