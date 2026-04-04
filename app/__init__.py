import logging
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

from app.database import init_db
from app.routes import register_routes


def create_app(database=None):
    load_dotenv()

    app = Flask(__name__)

    # Structured JSON logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    ))
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)
    logging.getLogger("werkzeug").handlers = [handler]

    # Prometheus metrics at /metrics
    PrometheusMetrics(app)

    init_db(app, database=database)

    from app import models  # noqa: F401

    register_routes(app)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/logs")
    def logs():
        import subprocess
        try:
            result = subprocess.run(
                ["tail", "-n", "100", "/proc/1/fd/1"],
                capture_output=True, text=True, timeout=3
            )
            lines = result.stdout or "No logs available"
        except Exception:
            lines = "Log access unavailable in this environment"
        return app.response_class(lines, mimetype="text/plain")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
