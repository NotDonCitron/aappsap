"""WSGI entry point for production servers."""

import os
import sys
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)
os.chdir(project_dir)

logger.info(f"Project dir: {project_dir}")
logger.info(f"Python path: {sys.path[0]}")

# Set environment
os.environ["FLASK_ENV"] = "production"
logger.info("FLASK_ENV set to production")

# Create minimal app first (always works)
from flask import Flask, jsonify

app = Flask(__name__)

logger.info("Minimal Flask app created")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "aappsap"}), 200


@app.route("/ready", methods=["GET"])
def ready():
    return jsonify({"status": "ready", "service": "aappsap"}), 200


@app.route("/api/v1/test", methods=["GET"])
def test():
    return jsonify({"message": "Hello from aappsap!", "status": "operational"}), 200


logger.info("Minimal routes registered")

# Try to upgrade to full app
try:
    from app import create_app

    logger.info("Attempting to create full app...")
    full_app = create_app("production")
    logger.info("Full app created successfully")

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
            logger.info(f"Added route: {rule.rule}")

    logger.info("All routes from full app copied")
except Exception as e:
    logger.error(f"Failed to load full app: {e}")
    logger.info("Using minimal app only")

if __name__ == "__main__":
    app.run()
