"""
Cliente Roboflow — singleton para reutilizar el modelo.
Soporta tanto hosted inference (API) como modelo local YOLOv8.
"""

import os
import logging

logger = logging.getLogger(__name__)

_model = None


def get_model():
    global _model
    if _model is not None:
        return _model

    api_key     = os.environ["ROBOFLOW_API_KEY"]
    project     = os.environ.get("ROBOFLOW_PROJECT", "reconocimiento-de-piezas-rllp1")
    version_num = int(os.environ.get("ROBOFLOW_VERSION", "4"))

    # Intentar primero con inference SDK (hosted) — más ligero en Render free tier
    try:
        from inference_sdk import InferenceHTTPClient
        _model = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=api_key,
        )
        # Guardar proyecto/versión para usarlo en predict
        _model._rf_project = project
        _model._rf_version = version_num
        _model._mode = "inference_sdk"
        logger.info("Modelo cargado via inference_sdk (hosted)")
        return _model
    except ImportError:
        pass

    # Fallback: Roboflow SDK clásico
    try:
        from roboflow import Roboflow
        rf = Roboflow(api_key=api_key)
        workspace = rf.workspace()
        proj = workspace.project(project)
        _model = proj.version(version_num).model
        if _model is not None:
            _model._mode = "roboflow_sdk"
            logger.info("Modelo cargado via roboflow SDK")
            return _model
    except Exception as e:
        logger.error("roboflow SDK falló: %s", e)

    raise RuntimeError("No se pudo cargar el modelo. Verifica ROBOFLOW_API_KEY, ROBOFLOW_PROJECT y ROBOFLOW_VERSION.")
