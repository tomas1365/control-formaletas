"""
UNISPAN — Backend Flask
Punto de entrada: create_app()
"""

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Config
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Blueprints
    from app.routes.detection import detection_bp
    from app.routes.catalog import catalog_bp
    from app.routes.history import history_bp
    from app.routes.operators import operators_bp

    app.register_blueprint(detection_bp, url_prefix="/api/detect")
    app.register_blueprint(catalog_bp, url_prefix="/api/catalog")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(operators_bp, url_prefix="/api/operators")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "unispan-backend"}

    return app
