"""
Ruta de detección — usa API REST de Roboflow directamente.
"""

import uuid
import time
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.utils.roboflow_client import predict_image
from app.utils.piece_mapper import map_detections_to_specs

detection_bp = Blueprint("detection", __name__)
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@detection_bp.post("/")
def detect():
    if "image" not in request.files:
        return jsonify({"error": "No se recibió imagen"}), 400

    file = request.files["image"]
    operator_id = request.form.get("operator_id", "DESCONOCIDO")

    if not file or not _allowed(file.filename):
        return jsonify({"error": "Formato no permitido. Use PNG, JPG o WEBP"}), 415

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    save_path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    file.save(save_path)

    try:
        t0 = time.perf_counter()
        predictions = predict_image(str(save_path))
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        enriched = map_detections_to_specs(predictions)

        return jsonify({
            "ok": True,
            "operator_id": operator_id,
            "image_file": filename,
            "inference_ms": elapsed_ms,
            "total_detected": len(predictions),
            "pieces": enriched,
        })

    except Exception as exc:
        current_app.logger.error("Detection error: %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500

    finally:
        _cleanup_old_uploads(current_app.config["UPLOAD_FOLDER"], max_files=500)


def _cleanup_old_uploads(folder: str, max_files: int):
    files = sorted(Path(folder).iterdir(), key=lambda f: f.stat().st_mtime)
    if len(files) > max_files:
        for f in files[: len(files) - max_files]:
            f.unlink(missing_ok=True)
