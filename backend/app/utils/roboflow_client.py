"""
Cliente Roboflow — singleton para reutilizar el modelo en caliente.
"""

import os
from roboflow import Roboflow

_model = None


def get_model():
    global _model
    if _model is not None:
        return _model

    api_key = os.environ["ROBOFLOW_API_KEY"]
    project_name = os.environ.get("ROBOFLOW_PROJECT", "reconocimiento-de-piezas")
    version_num = int(os.environ.get("ROBOFLOW_VERSION", "1"))

    rf = Roboflow(api_key=api_key)
    project = rf.workspace().project(project_name)
    _model = project.version(version_num).model

    return _model
