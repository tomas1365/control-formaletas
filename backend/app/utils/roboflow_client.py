"""
Cliente Roboflow via API REST — sin dependencias adicionales.
Usa requests directamente contra la Roboflow Hosted Inference API.
"""

import os
import base64
import requests
import logging

logger = logging.getLogger(__name__)


def predict_image(image_path: str) -> list[dict]:
    """
    Envía imagen a Roboflow Hosted Inference y retorna predicciones.
    No requiere roboflow SDK ni inference-sdk — solo requests.
    """
    api_key  = os.environ["ROBOFLOW_API_KEY"]
    project  = os.environ.get("ROBOFLOW_PROJECT", "reconocimiento-de-piezas-rllp1")
    version  = os.environ.get("ROBOFLOW_VERSION", "4")

    # Leer y codificar imagen en base64
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://detect.roboflow.com/{project}/{version}"
    params = {"api_key": api_key}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(
        url,
        params=params,
        data=img_b64,
        headers=headers,
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(f"Roboflow API error {response.status_code}: {response.text}")

    data = response.json()
    logger.info("Roboflow response: %s predictions", len(data.get("predictions", [])))
    return data.get("predictions", [])
