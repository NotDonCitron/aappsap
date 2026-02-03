"""WSGI entry point for production servers."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

# Get environment from ENV, default to production
env = os.environ.get("FLASK_ENV", "production")
app = create_app(env)

# Auto-initialize database on startup
with app.app_context():
    db.create_all()
    print("✅ Database tables created")

    # Auto-seed if requested
    if os.environ.get("SEED_ON_STARTUP", "").lower() == "true":
        try:
            from scripts.seed import seed_database

            seed_database()
            print("✅ Database seeded")
        except Exception as e:
            print(f"⚠️  Seeding failed: {e}")

if __name__ == "__main__":
    app.run()
