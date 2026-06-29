"""
Servicio de detección — soporta inference_sdk (hosted) y roboflow SDK clásico.
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


def _run_inference(model, image_path: str, project: str, version: int) -> list[dict]:
    """Ejecuta inferencia según el modo del modelo."""
    mode = getattr(model, "_mode", "roboflow_sdk")

    if mode == "inference_sdk":
        result = model.infer(
            image_path,
            model_id=f"{project}/{version}",
        )
        # inference_sdk retorna objeto con .predictions
        if hasattr(result, "predictions"):
            preds = result.predictions
        elif isinstance(result, dict):
            preds = result.get("predictions", [])
        elif isinstance(result, list) and len(result) > 0:
            # lista de resultados por imagen
            first = result[0]
            preds = getattr(first, "predictions", first.get("predictions", []) if isinstance(first, dict) else [])
        else:
            preds = []

        # Normalizar a formato estándar
        normalized = []
        for p in preds:
            if hasattr(p, "class_name"):
                normalized.append({
                    "class": p.class_name,
                    "confidence": p.confidence,
                    "x": p.x, "y": p.y,
                    "width": p.width, "height": p.height,
                })
            elif isinstance(p, dict):
                normalized.append({
                    "class": p.get("class") or p.get("class_name", ""),
                    "confidence": p.get("confidence", 0),
                    "x": p.get("x", 0), "y": p.get("y", 0),
                    "width": p.get("width", 0), "height": p.get("height", 0),
                })
        return normalized

    else:
        # roboflow SDK clásico
        result = model.predict(image_path, confidence=40, overlap=30).json()
        return result.get("predictions", [])


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
        model = get_model()

        project = os.environ.get("ROBOFLOW_PROJECT", "reconocimiento-de-piezas-rllp1")
        version = int(os.environ.get("ROBOFLOW_VERSION", "4"))

        predictions = _run_inference(model, str(save_path), project, version)
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
