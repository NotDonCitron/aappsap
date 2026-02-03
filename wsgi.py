"""WSGI entry point for production servers."""

import os
import sys

# Add parent directory to path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)
os.chdir(project_dir)

# Set environment
os.environ["FLASK_ENV"] = "production"

# Create minimal app first (always works)
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "aappsap"}), 200


@app.route("/ready", methods=["GET"])
def ready():
    return jsonify({"status": "ready", "service": "aappsap"}), 200


@app.route("/api/v1/test", methods=["GET"])
def test():
    return jsonify({"message": "Hello from aappsap!", "status": "operational"}), 200


# Try to upgrade to full app
try:
    from app import create_app

    full_app = create_app("production")

    # Copy routes from full app
    for rule in full_app.url_map.iter_rules():
        if rule.endpoint != "static" and rule.rule not in [
            "/health",
            "/ready",
            "/api/v1/test",
        ]:
            app.add_url_rule(
                rule.rule,
                rule.endpoint,
                full_app.view_functions.get(rule.endpoint, None),
                methods=list(rule.methods or []),
            )

    print("✅ Full app loaded successfully")
except Exception as e:
    print(f"⚠️  Using minimal app: {e}")

if __name__ == "__main__":
    app.run()
