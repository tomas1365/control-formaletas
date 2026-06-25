import json
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify

operators_bp = Blueprint("operators", __name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "operators.json"
DB_PATH.parent.mkdir(exist_ok=True)

SEED = [
    {"id": "OP-001", "name": "Carlos Ramírez", "role": "Técnico Senior", "active": True},
    {"id": "OP-002", "name": "Ana Torres",     "role": "Técnico",        "active": True},
    {"id": "OP-003", "name": "Luis Mendez",    "role": "Inspector",      "active": True},
]


def _load() -> list[dict]:
    if not DB_PATH.exists():
        _save(SEED)
        return SEED
    return json.loads(DB_PATH.read_text())


def _save(records: list[dict]):
    DB_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2))


@operators_bp.get("/")
def get_operators():
    records = _load()
    return jsonify({"ok": True, "operators": records})


@operators_bp.post("/")
def add_operator():
    body = request.json or {}
    record = {"id": f"OP-{str(uuid.uuid4())[:4].upper()}", "active": True, **body}
    records = _load()
    records.append(record)
    _save(records)
    return jsonify({"ok": True, "operator": record}), 201


@operators_bp.patch("/<op_id>")
def update_operator(op_id: str):
    body = request.json or {}
    records = _load()
    for r in records:
        if r["id"] == op_id:
            r.update(body)
    _save(records)
    return jsonify({"ok": True})
