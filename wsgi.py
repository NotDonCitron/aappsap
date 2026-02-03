"""WSGI entry point for production servers."""

import os
from app import create_app, db

# Get environment from ENV, default to production
env = os.environ.get("FLASK_ENV", "production")
app = create_app(env)

# Auto-initialize database on startup
with app.app_context():
    db.create_all()
    print("✅ Database tables created")

if __name__ == "__main__":
    app.run()
