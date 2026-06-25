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
}

# Alias: si Roboflow entrenó con nombres distintos, mapearlos aquí
CLASS_ALIAS: dict[str, str] = {
    "panel_muro_50":    "PM-050",
    "panel_muro_60":    "PM-060",
    "panel_muro_75":    "PM-075",
    "panel_muro_90":    "PM-090",
    "panel_muro_120":   "PM-120",
    "panel_muro_150":   "PM-150",
    "pma_50":  "PMA-050",
    "pma_75":  "PMA-075",
    "pma_120": "PMA-120",
    "ei_50":   "EI-050",
    "ei_75":   "EI-075",
    "ei_120":  "EI-120",
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
