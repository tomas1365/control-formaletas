"""
Mapea las clases detectadas por Roboflow a las especificaciones
oficiales UNISPAN Colombia.

Fuente: UNISPAN_Catalogo_Formaleta.xlsx — 199 referencias
  - Paneles Tipo A (ancho ≥300mm): 60 refs  → prefijo PM
  - Paneles Tipo B (ancho <300mm): 54 refs   → prefijo PB
  - Esquineros Internos 150×150mm: 85 refs   → prefijo EI
"""

# ── Catálogo completo UNISPAN ────────────────────────────────────────────────
# Formato: "CODIGO": {family, largo_mm, ancho_mm, area_m2, tipo, ref_horiz, ref_platina, material}

PIECE_SPECS: dict[str, dict] = {}

# ── Panel Muro Tipo A (ancho ≥300mm) — 60 referencias ───────────────────────
_PM_LARGOS = [
    (2400, 3), (1200, 2), (900, 2), (800, 1), (750, 1), (600, 1)
]
_PM_ANCHOS = [600, 550, 500, 450, 420, 400, 380, 350, 320, 300]

for largo, ref_h in _PM_LARGOS:
    for ancho in _PM_ANCHOS:
        code = f"PM-{largo}x{ancho}"
        PIECE_SPECS[code] = {
            "family": "PM",
            "tipo": "Panel Muro Tipo A",
            "largo_mm": largo,
            "ancho_mm": ancho,
            "area_m2": round(largo * ancho / 1_000_000, 4),
            "estructura": "Tipo A (≥300mm)",
            "ref_horiz": ref_h,
            "ref_platina": None,
            "material": "Acero carbono 3mm",
        }

# ── Panel Borde Tipo B (ancho <300mm) — 54 referencias ──────────────────────
_PB_LARGOS = [
    (2400, 5), (1200, 4), (900, 3), (800, 3), (750, 2), (600, 2)
]
_PB_ANCHOS = [270, 250, 230, 200, 150, 120, 100, 90, 80]

for largo, ref_p in _PB_LARGOS:
    for ancho in _PB_ANCHOS:
        code = f"PB-{largo}x{ancho}"
        PIECE_SPECS[code] = {
            "family": "PB",
            "tipo": "Panel Borde Tipo B",
            "largo_mm": largo,
            "ancho_mm": ancho,
            "area_m2": round(largo * ancho / 1_000_000, 4),
            "estructura": "Tipo B (<300mm)",
            "ref_horiz": None,
            "ref_platina": ref_p,
            "material": "Acero carbono 3mm",
        }

# ── Esquineros Internos 150×150mm — 5 largos ────────────────────────────────
_EI_LARGOS = [
    (2400, None),  # ref por definir según catálogo
    (1200, 4),
    (900,  3),
    (800,  3),
    (600,  2),
]

for largo, ref_i in _EI_LARGOS:
    code = f"EI-{largo}x150x150"
    PIECE_SPECS[code] = {
        "family": "EI",
        "tipo": "Esquinero Interno",
        "largo_mm": largo,
        "ancho1_mm": 150,
        "ancho2_mm": 150,
        "area_m2": round(largo * 150 / 1_000_000 * 2, 4),  # dos caras
        "estructura": "150×150mm",
        "ref_internos": ref_i,
        "material": "Acero carbono 3mm",
        "observacion": "Dos caras 150mm",
    }

# ── Piezas especiales detectadas en Roboflow ────────────────────────────────
PIECE_SPECS["UM-1200x200x150"] = {
    "family": "UM",
    "tipo": "Viga U Metálica",
    "largo_mm": 1200,
    "ancho_mm": 200,
    "alto_mm": 150,
    "material": "Acero carbono 3mm",
}
PIECE_SPECS["GENERICO"] = {
    "family": "GEN",
    "tipo": "Pieza sin clasificar",
    "material": "Acero carbono 3mm",
}
PIECE_SPECS["NULO"] = {
    "family": "NULL",
    "tipo": "Anotación vacía en dataset",
}


# ── CLASS_ALIAS — nombres exactos de Roboflow → código UNISPAN ──────────────
# Las clases actuales del proyecto reconocimiento-de-piezas son:
#   EI  |  null  |  PM  |  Reconocimiento-de-Piezas  |  UM 1200 × 200 × 150
#
# IMPORTANTE: cuando el modelo sea reentrenado con clases específicas
# (ej. "PM-2400x600"), agregar los alias aquí.

CLASS_ALIAS: dict[str, str] = {
    # Clases actuales del modelo (genéricas)
    "ei":                        "EI-1200x150x150",   # largo más común
    "pm":                        "PM-1200x500",        # largo/ancho más común
    "um_1200_×_200_×_150":       "UM-1200x200x150",
    "um 1200 × 200 × 150":       "UM-1200x200x150",
    "reconocimiento-de-piezas":  "GENERICO",
    "reconocimiento_de_piezas":  "GENERICO",
    "null":                      "NULO",
    # Aliases por si el modelo retorna variaciones
    "panel_muro":                "PM-1200x500",
    "panel_borde":               "PB-1200x200",
    "esquinero":                 "EI-1200x150x150",
    "esquinero_interno":         "EI-1200x150x150",
}


def map_detections_to_specs(predictions: list[dict]) -> list[dict]:
    """
    Recibe lista de predicciones de Roboflow y retorna lista enriquecida
    con specs UNISPAN del catálogo oficial.
    """
    enriched = []
    for pred in predictions:
        raw_class = pred.get("class", "")
        # Normalizar para búsqueda en alias
        normalized = raw_class.lower().replace(" ", "_")
        # Buscar alias primero, luego intentar código directo
        code = CLASS_ALIAS.get(normalized) or CLASS_ALIAS.get(raw_class.lower()) or raw_class.upper()
        specs = PIECE_SPECS.get(code, {})

        enriched.append({
            "code": code,
            "raw_class": raw_class,
            "confidence": round(pred.get("confidence", 0) * 100, 1),
            "bbox": {
                "x": pred.get("x"),
                "y": pred.get("y"),
                "width": pred.get("width"),
                "height": pred.get("height"),
            },
            "specs": specs,
            "known": bool(specs),
        })
    return enriched


def get_catalog_list() -> list[dict]:
    """Retorna el catálogo completo como lista para el endpoint /api/catalog/"""
    return [{"code": k, **v} for k, v in PIECE_SPECS.items()]
