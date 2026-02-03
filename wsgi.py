"""WSGI entry point for production servers."""

import os
from flask import Flask, jsonify

# Create Flask app directly
app = Flask(__name__)


# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "aappsap"}), 200


# Ready check
@app.route("/ready", methods=["GET"])
def ready():
    return jsonify({"status": "ready", "service": "aappsap"}), 200


# Test endpoint
@app.route("/api/v1/test", methods=["GET"])
def test():
    return jsonify(
        {"message": "Hello from aappsap!", "status": "operational", "version": "1.0.0"}
    ), 200


# Root endpoint
@app.route("/", methods=["GET"])
def root():
    return jsonify(
        {
            "service": "aappsap API",
            "version": "1.0.0",
            "endpoints": ["/health", "/ready", "/api/v1/test"],
        }
    ), 200


if __name__ == "__main__":
    app.run()
