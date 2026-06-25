"""
Historial de auditorías — almacenamiento JSON local.
Reemplazable por PostgreSQL sin cambiar la interfaz.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from flask import Blueprint, request, jsonify

history_bp = Blueprint("history", __name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "history.json"
DB_PATH.parent.mkdir(exist_ok=True)


def _load() -> list[dict]:
    if not DB_PATH.exists():
        return []
    return json.loads(DB_PATH.read_text())


def _save(records: list[dict]):
    DB_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2))


@history_bp.post("/")
def add_record():
    body = request.json or {}
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **body,
    }
    records = _load()
    records.insert(0, record)
    _save(records)
    return jsonify({"ok": True, "id": record["id"]}), 201


@history_bp.get("/")
def get_history():
    operator = request.args.get("operator_id")
    limit = int(request.args.get("limit", 100))
    records = _load()
    if operator:
        records = [r for r in records if r.get("operator_id") == operator]
    return jsonify({"ok": True, "total": len(records), "records": records[:limit]})


@history_bp.delete("/<record_id>")
def delete_record(record_id: str):
    records = _load()
    records = [r for r in records if r["id"] != record_id]
    _save(records)
    return jsonify({"ok": True})
