"""WSGI entry point for production servers."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Get environment from ENV, default to production
env = os.environ.get("FLASK_ENV", "production")
app = create_app(env)

if __name__ == "__main__":
    app.run()
