"""Simple WSGI entry point for aappsap."""

from flask import Flask, jsonify

application = app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"service": "aappsap", "version": "1.0.0", "status": "running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/ready")
def ready():
    return jsonify({"status": "ready"})


@app.route("/api/v1/test")
def test():
    return jsonify({"message": "Hello from aappsap!", "status": "operational"})
