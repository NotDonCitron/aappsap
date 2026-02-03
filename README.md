# Secure Order Management System 🛡️

A production-ready Flask-based order management API with JWT authentication, automatic stock reservation, email notifications, webhooks, and role-based access control.

## Features

- 🔐 **JWT Authentication** - Access tokens (1h) + Refresh tokens (7 days)
- 👥 **Role-Based Access Control** - Admin, Manager, and Customer roles
- 📦 **Inventory Management** - Automatic stock reservation and release
- 📧 **Email Notifications** - Order confirmations and shipping alerts
- 🔗 **Webhooks** - HMAC-signed event delivery
- 📊 **Reports & Analytics** - CSV export, sales summaries
- 🧪 **Comprehensive Tests** - pytest with coverage

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configuration

Edit `.env` file with your settings:

```bash
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database (SQLite for development)
DEV_DATABASE_URL=sqlite:///dev.db

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Initialize Database

```bash
# Create tables
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Seed with test data
python scripts/seed.py
```

### 4. Run Server

```bash
flask run
```

## API Documentation

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login (rate limited: 5/min) |
| `/api/v1/auth/refresh` | POST | Refresh access token |
| `/api/v1/auth/logout` | POST | Revoke token |
| `/api/v1/auth/me` | GET | Get current user |

### Inventory

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/inventory/products` | GET | Any | List products (with filters) |
| `/api/v1/inventory/products` | POST | Manager+ | Create product |
| `/api/v1/inventory/products/<id>` | GET | Any | Get product |
| `/api/v1/inventory/products/<id>` | PUT | Manager+ | Update product |
| `/api/v1/inventory/products/<id>/stock` | PATCH | Manager+ | Adjust stock |
| `/api/v1/inventory/categories` | GET | Any | List categories |

### Orders

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/orders` | GET | Any | List orders |
| `/api/v1/orders` | POST | Any | Create order |
| `/api/v1/orders/<id>` | GET | Any | Get order |
| `/api/v1/orders/<id>/cancel` | POST | Any | Cancel order |
| `/api/v1/orders/<id>/confirm` | POST | Manager+ | Confirm order |

### Admin

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/admin/users` | GET | Admin | List users |
| `/api/v1/admin/users/<id>/role` | PATCH | Admin | Change role |
| `/api/v1/admin/stats` | GET | Admin | System statistics |

### Reports

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/reports/sales` | GET | Manager+ | Sales summary |
| `/api/v1/reports/inventory` | GET | Manager+ | Inventory status |
| `/api/v1/reports/export/orders` | GET | Manager+ | Export CSV |

## Example Usage

### Register & Login

```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123","first_name":"John"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123"}'
```

### Create Order

```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ],
    "shipping_cost": 10.00
  }'
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific module
pytest tests/test_orders.py -v
```

## Project Structure

```
secure_order_system/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── inventory.py
│   │   ├── orders.py
│   │   ├── admin.py
│   │   └── reports.py
│   ├── services/            # Business logic
│   │   ├── email_service.py
│   │   ├── webhook_service.py
│   │   └── report_service.py
│   └── utils/               # Utilities
│       └── decorators.py
├── tests/                   # Test suite
├── scripts/                 # Helper scripts
├── requirements.txt
├── run.py
└── README.md
```

## Security Features

- ✅ bcrypt with 12+ rounds for passwords
- ✅ JWT short expiry + refresh tokens
- ✅ Rate limiting on auth endpoints (5 req/minute)
- ✅ Account lockout after 5 failed attempts
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ CORS properly configured
- ✅ Audit logging for security events

## Production Deployment

1. Use PostgreSQL instead of SQLite
2. Configure Redis for rate limiting
3. Set up Celery for async tasks
4. Enable HTTPS
5. Use environment variables for secrets

```bash
# Example with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## License

MIT License
