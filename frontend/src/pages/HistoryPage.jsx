import { useState, useEffect } from "react";
import { RefreshCw, Download } from "lucide-react";
import { apiFetch } from "../utils/api";

export default function HistoryPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const d = await apiFetch("/api/history/?limit=200");
      setRecords(d.records);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const exportCSV = () => {
    const rows = [
      ["Timestamp", "Operador", "Piezas detectadas", "ms inferencia"],
      ...records.map((r) => [r.timestamp, r.operator_id, r.total_detected, r.inference_ms]),
    ];
    const csv = rows.map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `historial_unispan_${Date.now()}.csv`;
    a.click();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Historial de auditorías</h1>
          <p className="text-steel-400 text-sm mt-1">{records.length} registros</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="btn-ghost flex items-center gap-2">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Refrescar
          </button>
          <button onClick={exportCSV} className="btn-ghost flex items-center gap-2">
            <Download size={14} /> CSV
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-steel-600/40 text-steel-400 text-left">
              <th className="px-4 py-3">Fecha/Hora</th>
              <th className="px-4 py-3">Operador</th>
              <th className="px-4 py-3">Piezas</th>
              <th className="px-4 py-3">Inferencia</th>
              <th className="px-4 py-3">Códigos</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id} className="border-b border-steel-600/20 hover:bg-steel-700/20 transition-colors">
                <td className="px-4 py-3 font-mono text-xs text-steel-300">
                  {new Date(r.timestamp).toLocaleString("es-CO")}
                </td>
                <td className="px-4 py-3 text-steel-200">{r.operator_id}</td>
                <td className="px-4 py-3 text-amber-400 font-semibold">{r.total_detected}</td>
                <td className="px-4 py-3 text-steel-400 font-mono">{r.inference_ms} ms</td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {(r.pieces || []).slice(0, 4).map((p, i) => (
                      <span key={i} className="badge bg-steel-700 text-steel-300 font-mono">
                        {p.code}
                      </span>
                    ))}
                    {(r.pieces || []).length > 4 && (
                      <span className="badge bg-steel-700 text-steel-400">
                        +{r.pieces.length - 4}
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {records.length === 0 && !loading && (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center text-steel-500">
                  Sin auditorías registradas
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
