# AGENTS.md - Agentic Coding Instructions

## Project Overview

**test_shop** - Flask-based e-commerce order management system with JWT authentication, Firebase integration, and full-featured product/order/cart management.

**Stack**: Python 3.x, Flask, SQLAlchemy (SQLite), Flask-JWT-Extended, Firebase Admin SDK

## Project Structure

```
test_shop/
├── app/
│   ├── __init__.py          # App factory, blueprint registration
│   ├── models/__init__.py   # All database models (User, Product, Order, Cart, Review, etc.)
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # JWT authentication (login, register, refresh)
│   │   ├── products.py      # Product CRUD
│   │   ├── orders.py        # Order management with stock reservation
│   │   ├── cart.py          # Shopping cart endpoints
│   │   ├── reviews.py       # Product reviews and ratings
│   │   ├── shipping.py      # Shipping cost calculation
│   │   └── admin.py         # Admin endpoints (user search, product filter)
│   ├── services/            # Business logic services
│   └── utils/               # Helper utilities
├── config.py                # Environment-based configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── tests/                   # Test suite
```

## Database Models

### Core Models
- **User**: id, email, password_hash, role (admin/manager/customer), is_active
- **Product**: id, sku, name, price, stock, reserved_stock, weight_kg, category, is_active
- **Order**: id, user_id, status, total_amount, created_at
- **OrderItem**: id, order_id, product_id, quantity, price

### Feature Models
- **Cart**: id, user_id, items (relationship to CartItem)
- **CartItem**: id, cart_id, product_id, quantity
- **Review**: id, product_id, user_id, rating (1-5), comment, is_approved
- **ShippingRate**: id, name, base_cost, cost_per_kg, max_weight, is_active

## API Endpoints

### Authentication (`/api/v1/auth/*`)
- `POST /register` - User registration
- `POST /login` - JWT login (returns access + refresh tokens)
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user

### Products (`/api/v1/products/*`)
- `GET /` - List products (with pagination)
- `GET /<id>` - Get single product
- `POST /` - Create product (admin/manager)
- `PUT /<id>` - Update product
- `DELETE /<id>` - Delete product

### Orders (`/api/v1/orders/*`)
- `GET /` - List user orders
- `POST /` - Create order (with stock reservation)
- `GET /<id>` - Get order details
- `PUT /<id>/status` - Update order status

### Cart (`/api/v1/cart/*`)
- `GET /` - Get cart contents
- `POST /add` - Add item to cart
- `PUT /update/<item_id>` - Update quantity
- `DELETE /remove/<item_id>` - Remove item
- `DELETE /clear` - Clear cart

### Reviews (`/api/v1/reviews/*`)
- `POST /` - Create review (rating 1-5, comment)
- `GET /product/<product_id>` - Get reviews with pagination + stats

### Shipping (`/api/v1/shipping/*`)
- `POST /calculate` - Calculate shipping costs by cart items weight
- `GET /rates` - List active shipping rates

### Admin (`/api/v1/admin/*`)
- `GET /users?search=&role=&is_active=` - Search/filter users
- `GET /products/search?search=&category=&min_price=&max_price=&in_stock=` - Filter products

## Build / Test Commands

```bash
# Run the application
python run.py

# Run all tests
pytest

# Run specific test file
pytest tests/test_orders.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

## Code Style Guidelines

### Python
- **Indentation**: 4 spaces
- **Line Length**: 80 characters max
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Imports**: Group by stdlib, third-party, application
- **Docstrings**: Triple double quotes, include Args/Returns for public functions

### Error Handling
```python
# Use specific exceptions, never bare except
try:
    result = risky_operation()
except ValueError as e:
    return jsonify({'error': str(e)}), 400
except Exception as e:
    logger.exception("Unexpected error")
    return jsonify({'error': 'Internal error'}), 500
```

### JWT Auth Pattern
```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def protected_endpoint():
    user_id = int(get_jwt_identity())
    # ... handle request
```

## Critical Implementation Details

### Stock Reservation
Products have `stock` (total) and `reserved_stock` fields. When an order is created:
1. Validate sufficient available_stock (stock - reserved_stock)
2. Increment reserved_stock for each item
3. On order completion, decrement both stock and reserved_stock

### Weight-Based Shipping
Products have `weight_kg` field. Shipping calculation:
```python
total_weight = sum(item.product.weight_kg * item.quantity for item in items)
cost = rate.base_cost + (rate.cost_per_kg * total_weight)
```

### Review Approval
Reviews have `is_approved` flag. Only approved reviews are included in average rating calculation and public listings.

## Firebase Configuration

Project: `kek-setup-2026`
Services: Firestore, Auth, Storage, FCM

Credentials loaded from environment (not committed). Firebase integration used for:
- Push notifications (order status updates)
- Cloud Storage (product images)
- Firestore (sync/backup)

## Environment Variables

```bash
SECRET_KEY=<flask-secret>
JWT_SECRET_KEY=<jwt-secret>
DATABASE_URL=sqlite:///instance/shop.db
FIREBASE_CREDENTIALS_PATH=<path-to-service-account-json>
```

## Security Notes

- Never commit `.env` files or Firebase credentials
- All admin endpoints require `@jwt_required()` + role check
- Passwords hashed with werkzeug
- Input validated on all POST/PUT endpoints
