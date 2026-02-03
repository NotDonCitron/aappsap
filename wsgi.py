"""WSGI entry point for production servers."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create app based on environment
env = os.environ.get("FLASK_ENV", "production")

if env == "production":
    # Try to import the full app, fallback to minimal if it fails
    try:
        from app import create_app

        app = create_app("production")
    except Exception as e:
        print(f"⚠️  Failed to create full app: {e}")
        print("Using minimal app...")

        # Create minimal app
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "healthy", "service": "aappsap"}), 200

        @app.route("/api/v1/test", methods=["GET"])
        def test():
            return jsonify({"message": "Hello from aappsap!"}), 200
else:
    from app import create_app

    app = create_app(env)

if __name__ == "__main__":
    app.run()
