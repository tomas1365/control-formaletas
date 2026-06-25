import { useState, useEffect } from "react";
import { Plus, Pencil } from "lucide-react";
import { apiFetch } from "../utils/api";

export default function OperatorsPage() {
  const [operators, setOperators] = useState([]);
  const [adding, setAdding]       = useState(false);
  const [form, setForm]           = useState({ name: "", role: "" });

  const load = () =>
    apiFetch("/api/operators/").then((d) => setOperators(d.operators)).catch(console.error);

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!form.name) return;
    await fetch("/api/operators/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ name: "", role: "" });
    setAdding(false);
    load();
  };

  const toggleActive = async (op) => {
    await fetch(`/api/operators/${op.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ active: !op.active }),
    });
    load();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Operadores</h1>
          <p className="text-steel-400 text-sm mt-1">{operators.length} técnicos registrados</p>
        </div>
        <button onClick={() => setAdding(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Nuevo operador
        </button>
      </div>

      {adding && (
        <div className="card space-y-3 border-amber-500/30">
          <p className="font-semibold text-amber-400">Nuevo operador</p>
          <div className="grid sm:grid-cols-2 gap-3">
            <input
              className="input"
              placeholder="Nombre completo"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <input
              className="input"
              placeholder="Cargo (ej. Técnico Senior)"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setAdding(false)} className="btn-ghost">Cancelar</button>
            <button onClick={handleAdd} className="btn-primary">Guardar</button>
          </div>
        </div>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {operators.map((op) => (
          <div key={op.id} className="card flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-steel-400">{op.id}</span>
                <span className={`badge ${op.active ? "bg-ok/10 text-ok border-ok/30" : "bg-steel-700 text-steel-400"} border`}>
                  {op.active ? "Activo" : "Inactivo"}
                </span>
              </div>
              <p className="font-semibold text-steel-100">{op.name}</p>
              <p className="text-sm text-steel-400">{op.role}</p>
            </div>
            <button
              onClick={() => toggleActive(op)}
              className="text-steel-500 hover:text-steel-200 transition-colors mt-1"
              title="Cambiar estado"
            >
              <Pencil size={14} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
