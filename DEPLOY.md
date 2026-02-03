# Deployment Guide

## 1. Heroku (Easiest)

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-shop-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set JWT_SECRET_KEY="your-jwt-secret"
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Create database tables
heroku run "python -c 'from app import create_app, db; app = create_app(\"production\"); db.create_all()'"
```

## 2. Railway

1. Connect GitHub repo to Railway
2. Add PostgreSQL plugin
3. Set environment variables in dashboard
4. Deploy automatically on push

## 3. PythonAnywhere

```bash
# In PythonAnywhere Bash console
git clone <your-repo>
cd test_shop
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# In Web tab, configure:
# Source code: /home/yourusername/test_shop
# Working directory: /home/yourusername/test_shop
# WSGI: import from wsgi.py
```

## 4. VPS (DigitalOcean, Linode, etc.)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql

# Setup app
git clone <your-repo>
cd test_shop
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/testshop.service
```

**Service file:**
```ini
[Unit]
Description=Test Shop Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/test_shop
Environment="PATH=/var/www/test_shop/venv/bin"
Environment="SECRET_KEY=your-secret"
Environment="DATABASE_URL=postgresql://..."
ExecStart=/var/www/test_shop/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 "app:create_app('production')"

[Install]
WantedBy=multi-user.target
```

## Environment Variables Required

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | (Optional) For rate limiting |

## Database Migration

```bash
# Initialize migrations (first time)
flask db init

# Create migration
flask db migrate -m "initial"

# Apply
flask db upgrade
```
