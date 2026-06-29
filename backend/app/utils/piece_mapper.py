"""
Mapea las clases detectadas por Roboflow a las especificaciones
oficiales UNISPAN (PM, PMA, EI).
"""

# Especificaciones UNISPAN — fuente: catálogo técnico Tomas / Claude sessions
PIECE_SPECS = {
    # ── Panel Muro ──────────────────────────────────────────────────────
    "PM-050": {"family": "PM", "largo_cm": 50,  "ancho_cm": 50,  "refuerzos": 2, "material": "Acero carbono 3mm"},
    "PM-060": {"family": "PM", "largo_cm": 60,  "ancho_cm": 50,  "refuerzos": 2, "material": "Acero carbono 3mm"},
    "PM-075": {"family": "PM", "largo_cm": 75,  "ancho_cm": 50,  "refuerzos": 3, "material": "Acero carbono 3mm"},
    "PM-090": {"family": "PM", "largo_cm": 90,  "ancho_cm": 50,  "refuerzos": 3, "material": "Acero carbono 3mm"},
    "PM-120": {"family": "PM", "largo_cm": 120, "ancho_cm": 50,  "refuerzos": 4, "material": "Acero carbono 3mm"},
    "PM-150": {"family": "PM", "largo_cm": 150, "ancho_cm": 50,  "refuerzos": 5, "material": "Acero carbono 3mm"},
    # ── Panel Muro Angosto ───────────────────────────────────────────────
    "PMA-050": {"family": "PMA", "largo_cm": 50,  "ancho_cm": 25, "refuerzos": 2, "material": "Acero carbono 3mm"},
    "PMA-075": {"family": "PMA", "largo_cm": 75,  "ancho_cm": 25, "refuerzos": 3, "material": "Acero carbono 3mm"},
    "PMA-120": {"family": "PMA", "largo_cm": 120, "ancho_cm": 25, "refuerzos": 4, "material": "Acero carbono 3mm"},
    # ── Esquinero Interno ────────────────────────────────────────────────
    "EI-050": {"family": "EI", "largo_cm": 50,  "ancho_cm": 20, "refuerzos": 2, "material": "Acero carbono 3mm"},
    "EI-075": {"family": "EI", "largo_cm": 75,  "ancho_cm": 20, "refuerzos": 3, "material": "Acero carbono 3mm"},
    "EI-120": {"family": "EI", "largo_cm": 120, "ancho_cm": 20, "refuerzos": 4, "material": "Acero carbono 3mm"},
    # ── Viga UM (clase detectada en Roboflow) ────────────────────────────
    "UM-1200": {"family": "UM", "largo_cm": 120, "ancho_cm": 20, "alto_cm": 15, "refuerzos": 0, "material": "Acero carbono 3mm"},
    # ── Clases especiales ────────────────────────────────────────────────
    "GENERICO": {"family": "GEN", "descripcion": "Pieza sin clasificar específica", "material": "Acero carbono 3mm"},
    "NULO":     {"family": "NULL", "descripcion": "Anotación vacía en dataset"},
}

# Alias: nombres exactos de clases entrenadas en Roboflow
# Proyecto: reconocimiento-de-piezas (139 imágenes)
# Clases detectadas: EI, null, PM, Reconocimiento-de-Piezas, UM 1200 × 200 × 150
CLASS_ALIAS: dict[str, str] = {
    # ── Clases reales de Roboflow (tal como vienen en la respuesta) ──────
    "ei":                        "EI-050",   # Esquinero Interno — dimensión por confirmar
    "pm":                        "PM-120",   # Panel Muro — dimensión por confirmar
    "um_1200_×_200_×_150":       "UM-1200",  # Viga UM 1200×200×150
    "um 1200 × 200 × 150":       "UM-1200",
    "reconocimiento-de-piezas":  "GENERICO", # Clase genérica de proyecto
    "reconocimiento_de_piezas":  "GENERICO",
    "null":                      "NULO",     # Anotación vacía / sin clase

    # ── Aliases legacy (por si acaso) ───────────────────────────────────
    "panel_muro":   "PM-120",
    "esquinero":    "EI-050",
}


def map_detections_to_specs(predictions: list[dict]) -> list[dict]:
    """
    Recibe lista de predicciones de Roboflow y retorna lista enriquecida
    con specs UNISPAN.
    """
    enriched = []
    for pred in predictions:
        raw_class = pred.get("class", "").lower().replace(" ", "_")
        code = CLASS_ALIAS.get(raw_class, raw_class.upper())
        specs = PIECE_SPECS.get(code, {})

        enriched.append(
            {
                "code": code,
                "confidence": round(pred.get("confidence", 0) * 100, 1),
                "bbox": {
                    "x": pred.get("x"),
                    "y": pred.get("y"),
                    "width": pred.get("width"),
                    "height": pred.get("height"),
                },
                "specs": specs,
                "known": bool(specs),
            }
        )
    return enriched
