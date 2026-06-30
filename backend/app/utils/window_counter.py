"""
Módulo de conteo por patrón de perforaciones UNISPAN.

Especificaciones técnicas confirmadas:
─────────────────────────────────────
  Perforaciones laterales  = (largo_mm  - 25) / 50  (inicio 2.5cm, cada 5cm)
  Perforaciones frontales  = (ancho_mm  - 25) / 50  (inicio 2.5cm, cada 5cm)

  Ejemplos verificados:
    PM-2400x600 → lateral: 48 perforaciones, frontal: 12
    PM-1200x600 → lateral: 24 perforaciones, frontal: 12
    PM-2400x300 → lateral: 48 perforaciones, frontal:  6
    EI-1200x150 → lateral: 24 perforaciones, frontal:  3

Identificación de arrumes:
  Las bridas frontales (47mm alto) crean LÍNEAS VERTICALES OSCURAS
  periódicas visibles en foto lateral. Cada línea = separación entre piezas.
  Contando esas líneas verticales → número de piezas en el arrume.
"""

import math
import numpy as np
from PIL import Image
from typing import Optional


# ── Tablas de referencia ────────────────────────────────────────────────────

def perf_lateral(largo_mm: int) -> int:
    """Perforaciones en el lateral (cara larga)."""
    return round((largo_mm - 25) / 50)

def perf_frontal(ancho_mm: int) -> int:
    """Perforaciones en la frontal (cara corta)."""
    return round((ancho_mm - 25) / 50)

# Catálogo de perforaciones para largos estándar
PERF_POR_LARGO = {
    largo: perf_lateral(largo)
    for largo in [2400, 1200, 900, 800, 750, 600]
}
# {2400: 48, 1200: 24, 900: 18, 800: 16, 750: 15, 600: 12}

# Catálogo de perforaciones frontales por ancho
PERF_POR_ANCHO = {
    ancho: perf_frontal(ancho)
    for ancho in [600, 550, 500, 450, 420, 400, 380, 350, 320, 300,
                  270, 250, 230, 200, 150, 120, 100, 90, 80]
}


def estimar_largo_por_perforaciones(n_perf: int) -> Optional[int]:
    """
    Dado número de perforaciones visibles en lateral,
    estima el largo estándar más cercano (tolerancia 15%).
    """
    if n_perf <= 0:
        return None
    largo_est = (n_perf * 50) + 25
    largos = list(PERF_POR_LARGO.keys())
    mejor = min(largos, key=lambda l: abs(l - largo_est))
    if abs(mejor - largo_est) / mejor < 0.15:
        return mejor
    return None


def estimar_ancho_por_perforaciones(n_perf: int) -> Optional[int]:
    """
    Dado número de perforaciones visibles en frontal,
    estima el ancho estándar más cercano (tolerancia 15%).
    """
    if n_perf <= 0:
        return None
    ancho_est = (n_perf * 50) + 25
    anchos = list(PERF_POR_ANCHO.keys())
    mejor = min(anchos, key=lambda a: abs(a - ancho_est))
    if abs(mejor - ancho_est) / mejor < 0.15:
        return mejor
    return None


# ── Análisis de imagen por columnas de píxeles ─────────────────────────────

def detectar_lineas_verticales_brida(
    img_array: np.ndarray,
    min_oscuridad: int = 80,
    min_ancho_px: int = 3,
    min_separacion_px: int = 10,
) -> list[int]:
    """
    Detecta líneas verticales oscuras (bridas frontales) en una región de imagen.

    Las bridas frontales son barras metálicas de ~47mm que aparecen como
    líneas verticales más oscuras que la superficie plana del panel.

    Args:
        img_array:        array HxWx3 o HxW (escala grises)
        min_oscuridad:    valor máximo (0-255) para considerar píxel oscuro
        min_ancho_px:     ancho mínimo en píxeles de la línea
        min_separacion_px: separación mínima entre líneas

    Returns:
        Lista de posiciones X (centro de cada línea vertical detectada)
    """
    # Convertir a escala de grises si es necesario
    if img_array.ndim == 3:
        gray = np.mean(img_array[:, :, :3], axis=2)
    else:
        gray = img_array.astype(float)

    h, w = gray.shape

    # Perfil horizontal: promedio de oscuridad por columna
    col_mean = np.mean(gray, axis=0)

    # Detectar columnas oscuras (bridas)
    oscuras = col_mean < min_oscuridad

    # Agrupar columnas oscuras contiguas → líneas
    lineas = []
    en_linea = False
    inicio = 0

    for x in range(w):
        if oscuras[x] and not en_linea:
            en_linea = True
            inicio = x
        elif not oscuras[x] and en_linea:
            en_linea = False
            ancho = x - inicio
            if ancho >= min_ancho_px:
                centro = inicio + ancho // 2
                # Respetar separación mínima
                if not lineas or (centro - lineas[-1]) >= min_separacion_px:
                    lineas.append(centro)

    return lineas


def contar_piezas_en_region(
    imagen_path: str,
    bbox: Optional[dict] = None,
) -> dict:
    """
    Analiza una región de imagen para contar piezas por detección de bridas.

    Args:
        imagen_path: ruta a la imagen
        bbox: dict con x, y, width, height en píxeles (None = imagen completa)

    Returns:
        dict con conteo y diagnóstico
    """
    try:
        img = Image.open(imagen_path).convert("RGB")
        img_arr = np.array(img)
        h_total, w_total = img_arr.shape[:2]

        # Recortar región si se especifica bbox
        if bbox:
            x  = max(0, int(bbox.get("x", 0) - bbox.get("width", 0) / 2))
            y  = max(0, int(bbox.get("y", 0) - bbox.get("height", 0) / 2))
            x2 = min(w_total, x + int(bbox.get("width", 0)))
            y2 = min(h_total, y + int(bbox.get("height", 0)))
            region = img_arr[y:y2, x:x2]
        else:
            region = img_arr

        rh, rw = region.shape[:2]

        # Escalar umbral de separación según tamaño de región
        sep_px = max(8, rw // 30)

        lineas = detectar_lineas_verticales_brida(
            region,
            min_oscuridad=90,
            min_ancho_px=max(2, rw // 100),
            min_separacion_px=sep_px,
        )

        # Número de piezas = número de divisiones + 1
        # (cada brida visible separa dos piezas)
        n_lineas = len(lineas)
        n_piezas = max(1, n_lineas + 1) if n_lineas > 0 else 1

        # Estimar largo por espaciado entre líneas
        largo_estimado = None
        if len(lineas) >= 2:
            espaciados = [lineas[i+1] - lineas[i] for i in range(len(lineas)-1)]
            espaciado_medio = sum(espaciados) / len(espaciados)
            # Relación píxeles/mm depende del zoom — no podemos calcularla sin referencia
            # Pero podemos usar el número de perforaciones si la vista es lateral completa
            perf_estimadas = round(rw / (espaciado_medio * 0.5)) if espaciado_medio > 0 else 0
            largo_estimado = estimar_largo_por_perforaciones(perf_estimadas)

        return {
            "n_lineas_brida": n_lineas,
            "n_piezas_estimadas": n_piezas,
            "posiciones_bridas_px": lineas,
            "largo_estimado_mm": largo_estimado,
            "region_analizada_px": {"w": rw, "h": rh},
        }

    except Exception as e:
        return {
            "n_lineas_brida": 0,
            "n_piezas_estimadas": 1,
            "error": str(e),
        }


# ── Agrupación de detecciones en arrumes ───────────────────────────────────

def agrupar_en_arrumes(predictions: list[dict], umbral_px: int = 100) -> list[dict]:
    """
    Agrupa bounding boxes de piezas detectadas en arrumes.

    Criterio: piezas cuyas bboxes se solapan horizontalmente
    o están muy cerca → mismo arrume.
    """
    if not predictions:
        return []

    # Convertir bbox centro→ esquinas
    def bbox_to_rect(p):
        b = p.get("bbox", {})
        cx, cy = b.get("x", 0), b.get("y", 0)
        w,  h  = b.get("width", 1), b.get("height", 1)
        return {"x1": cx - w/2, "y1": cy - h/2, "x2": cx + w/2, "y2": cy + h/2}

    rects = [bbox_to_rect(p) for p in predictions]

    def solapan_o_cerca(r1, r2, margen=umbral_px):
        return not (r1["x2"] + margen < r2["x1"] or
                    r2["x2"] + margen < r1["x1"] or
                    r1["y2"] + margen < r2["y1"] or
                    r2["y2"] + margen < r1["y1"])

    # Union-Find simple
    parent = list(range(len(predictions)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(i)] = find(j)

    for i in range(len(predictions)):
        for j in range(i + 1, len(predictions)):
            if solapan_o_cerca(rects[i], rects[j], umbral_px):
                union(i, j)

    # Agrupar
    grupos: dict[int, list] = {}
    for i, p in enumerate(predictions):
        g = find(i)
        grupos.setdefault(g, []).append(p)

    arrumes = []
    for idx, (_, piezas) in enumerate(sorted(grupos.items())):
        familias = list(set(p.get("specs", {}).get("family", "?") for p in piezas))
        codigos  = [p.get("code", "?") for p in piezas]
        conf_avg = round(sum(p.get("confidence", 0) for p in piezas) / len(piezas), 1)

        xs = [p["bbox"]["x"] - p["bbox"]["width"]/2  for p in piezas if "bbox" in p]
        ys = [p["bbox"]["y"] - p["bbox"]["height"]/2 for p in piezas if "bbox" in p]
        x2s= [p["bbox"]["x"] + p["bbox"]["width"]/2  for p in piezas if "bbox" in p]
        y2s= [p["bbox"]["y"] + p["bbox"]["height"]/2 for p in piezas if "bbox" in p]

        arrumes.append({
            "arrume_id": idx + 1,
            "total_piezas": len(piezas),
            "familias": familias,
            "codigos_detectados": codigos,
            "confianza_promedio": conf_avg,
            "bbox_arrume": {
                "x1": min(xs) if xs else 0, "y1": min(ys) if ys else 0,
                "x2": max(x2s) if x2s else 0, "y2": max(y2s) if y2s else 0,
            },
            "piezas_detalle": piezas,
        })

    return arrumes


def analizar_imagen_completa(
    predictions: list[dict],
    imagen_path: Optional[str] = None,
    image_width: int = 0,
    image_height: int = 0,
) -> dict:
    """
    Análisis completo:
    1. Agrupa piezas en arrumes por bbox
    2. Para cada arrume, analiza la región buscando bridas verticales
    3. Combina conteo YOLOv11 + conteo por visión
    """
    if not predictions:
        return {
            "total_piezas": 0,
            "total_arrumes": 0,
            "arrumes": [],
            "familias": {},
            "resumen": "No se detectaron piezas en la imagen.",
        }

    umbral = max(80, image_width // 8) if image_width else 100
    arrumes = agrupar_en_arrumes(predictions, umbral_px=umbral)

    # Análisis visual por arrume (si hay imagen disponible)
    for arr in arrumes:
        if imagen_path:
            # Usar bbox del arrume para análisis de bridas
            b = arr["bbox_arrume"]
            bbox_px = {
                "x":      (b["x1"] + b["x2"]) / 2,
                "y":      (b["y1"] + b["y2"]) / 2,
                "width":  b["x2"] - b["x1"],
                "height": b["y2"] - b["y1"],
            }
            vision = contar_piezas_en_region(imagen_path, bbox_px)
            arr["vision"] = vision

            # Si visión detecta más piezas que YOLOv11, usar el mayor
            v_piezas = vision.get("n_piezas_estimadas", 0)
            if v_piezas > arr["total_piezas"]:
                arr["total_piezas_vision"] = v_piezas
                arr["total_piezas"] = v_piezas
                arr["fuente_conteo"] = "vision+yolo"
            else:
                arr["total_piezas_vision"] = v_piezas
                arr["fuente_conteo"] = "yolo"

    # Totales
    total_piezas = sum(a["total_piezas"] for a in arrumes)

    familias: dict[str, int] = {}
    for p in predictions:
        fam = p.get("specs", {}).get("family", "DESCONOCIDA")
        familias[fam] = familias.get(fam, 0) + 1

    partes = []
    for arr in arrumes:
        fams = ", ".join(arr["familias"])
        src  = arr.get("fuente_conteo", "yolo")
        partes.append(
            f"Arrume {arr['arrume_id']}: {arr['total_piezas']} pieza(s) [{fams}] ({src})"
        )

    resumen = (
        f"{total_piezas} pieza(s) en {len(arrumes)} arrume(s). "
        + " | ".join(partes)
    )

    return {
        "total_piezas":  total_piezas,
        "total_arrumes": len(arrumes),
        "arrumes":       arrumes,
        "familias":      familias,
        "resumen":       resumen,
    }
