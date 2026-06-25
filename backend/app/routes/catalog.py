from flask import Blueprint, jsonify
from app.utils.piece_mapper import PIECE_SPECS

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.get("/")
def get_catalog():
    items = [{"code": k, **v} for k, v in PIECE_SPECS.items()]
    return jsonify({"ok": True, "total": len(items), "pieces": items})


@catalog_bp.get("/<code>")
def get_piece(code: str):
    code = code.upper()
    specs = PIECE_SPECS.get(code)
    if not specs:
        return jsonify({"error": f"Pieza {code} no encontrada"}), 404
    return jsonify({"ok": True, "code": code, **specs})
