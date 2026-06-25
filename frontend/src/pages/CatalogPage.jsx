import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { apiFetch } from "../utils/api";

const FAMILY_COLOR = {
  PM:  "bg-blue-500/10 text-blue-400 border-blue-500/30",
  PMA: "bg-purple-500/10 text-purple-400 border-purple-500/30",
  EI:  "bg-amber-500/10 text-amber-400 border-amber-500/30",
};

export default function CatalogPage() {
  const [pieces, setPieces] = useState([]);
  const [query, setQuery]   = useState("");
  const [family, setFamily] = useState("ALL");

  useEffect(() => {
    apiFetch("/api/catalog/").then((d) => setPieces(d.pieces)).catch(console.error);
  }, []);

  const filtered = pieces.filter((p) => {
    const matchQ = p.code.includes(query.toUpperCase());
    const matchF = family === "ALL" || p.family === family;
    return matchQ && matchF;
  });

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold">Catálogo de piezas</h1>
        <p className="text-steel-400 text-sm mt-1">
          Especificaciones técnicas oficiales UNISPAN — acero carbono 3 mm
        </p>
      </div>

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-steel-500" />
          <input
            className="input pl-9"
            placeholder="Buscar código…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        {["ALL", "PM", "PMA", "EI"].map((f) => (
          <button
            key={f}
            onClick={() => setFamily(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors
              ${family === f
                ? "bg-amber-500 text-steel-900 border-amber-500"
                : "border-steel-600 text-steel-400 hover:text-steel-200"
              }`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((p) => (
          <div key={p.code} className="card space-y-3">
            <div className="flex items-center justify-between">
              <p className="font-mono font-semibold text-steel-100">{p.code}</p>
              <span className={`badge border ${FAMILY_COLOR[p.family] || ""}`}>{p.family}</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <Stat label="Largo" val={`${p.largo_cm} cm`} />
              <Stat label="Ancho" val={`${p.ancho_cm} cm`} />
              <Stat label="Refuerz." val={p.refuerzos} />
            </div>
            <p className="text-xs text-steel-500">{p.material}</p>
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="col-span-3 text-steel-500 text-sm text-center py-12">
            Sin resultados
          </p>
        )}
      </div>
    </div>
  );
}

function Stat({ label, val }) {
  return (
    <div className="bg-steel-900/60 rounded-lg p-2 text-center">
      <p className="text-steel-500 text-xs mb-0.5">{label}</p>
      <p className="font-semibold text-steel-100">{val}</p>
    </div>
  );
}
