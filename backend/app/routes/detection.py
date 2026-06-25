"""
Servicio de detección — YOLOv8 via Roboflow SDK
"""

import os
import uuid
import time
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.utils.roboflow_client import get_model
from app.utils.piece_mapper import map_detections_to_specs

detection_bp = Blueprint("detection", __name__)

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@detection_bp.post("/")
def detect():
    """
    POST /api/detect/
    Body: multipart/form-data  { image: <file>, operator_id: str }
    Returns: JSON con piezas detectadas + specs UNISPAN
    """
    if "image" not in request.files:
        return jsonify({"error": "No se recibió imagen"}), 400

    file = request.files["image"]
    operator_id = request.form.get("operator_id", "DESCONOCIDO")

    if not file or not _allowed(file.filename):
        return jsonify({"error": "Formato no permitido. Use PNG, JPG o WEBP"}), 415

    # Guardar temporalmente
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    save_path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    file.save(save_path)

    try:
        t0 = time.perf_counter()
        model = get_model()
        results = model.predict(str(save_path), confidence=40, overlap=30).json()
        elapsed_ms = round((time.perf_counter() - t0) * 1000)

        predictions = results.get("predictions", [])
        enriched = map_detections_to_specs(predictions)

        return jsonify(
            {
                "ok": True,
                "operator_id": operator_id,
                "image_file": filename,
                "inference_ms": elapsed_ms,
                "total_detected": len(predictions),
                "pieces": enriched,
            }
        )

    except Exception as exc:
        current_app.logger.error("Detection error: %s", exc)
        return jsonify({"error": str(exc)}), 500

    finally:
        # Mantener imagen para historial; limpiar > 500 archivos si es necesario
        _cleanup_old_uploads(current_app.config["UPLOAD_FOLDER"], max_files=500)


def _cleanup_old_uploads(folder: str, max_files: int):
    files = sorted(Path(folder).iterdir(), key=lambda f: f.stat().st_mtime)
    if len(files) > max_files:
        for f in files[: len(files) - max_files]:
            f.unlink(missing_ok=True)
