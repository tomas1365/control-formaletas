import { useState, useRef, useCallback } from "react";
import { Upload, Camera, Loader2, CheckCircle2, XCircle, AlertTriangle, Layers } from "lucide-react";
import { detectPiece } from "../utils/api";

const CONFIDENCE_COLOR = (c) =>
  c >= 80 ? "text-ok" : c >= 60 ? "text-amber-400" : "text-danger";

const FAMILY_COLOR = {
  PM:  "bg-blue-500/10 text-blue-400 border-blue-500/30",
  PB:  "bg-purple-500/10 text-purple-400 border-purple-500/30",
  EI:  "bg-amber-500/10 text-amber-400 border-amber-500/30",
  UM:  "bg-green-500/10 text-green-400 border-green-500/30",
};

export default function ScanPage() {
  const [operator, setOperator]   = useState("OP-001");
  const [preview, setPreview]     = useState(null);
  const [file, setFile]           = useState(null);
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);
  const inputRef = useRef();

  const handleFile = useCallback((f) => {
    if (!f) return;
    setFile(f);
    setResult(null);
    setError(null);
    setPreview(URL.createObjectURL(f));
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await detectPiece(file, operator);
      setResult(data);
      await fetch("/api/history/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operator_id: operator,
          image_file: data.image_file,
          inference_ms: data.inference_ms,
          total_detected: data.total_detected,
          pieces: data.pieces,
          analisis: data.analisis,
        }),
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold">Escaneo IA</h1>
        <p className="text-steel-400 text-sm mt-1">
          Captura una foto — YOLOv11 identifica piezas y cuenta arrumes.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        {/* ── Left — upload ── */}
        <div className="space-y-3">
          <div>
            <label className="text-sm text-steel-400 mb-1 block">Operador</label>
            <select value={operator} onChange={(e) => setOperator(e.target.value)} className="input">
              <option value="OP-001">OP-001 — Carlos Ramírez</option>
              <option value="OP-002">OP-002 — Ana Torres</option>
              <option value="OP-003">OP-003 — Luis Mendez</option>
            </select>
          </div>

          <div
            onClick={() => inputRef.current.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-steel-600 hover:border-amber-400 rounded-xl
                       flex flex-col items-center justify-center gap-3 p-8 cursor-pointer
                       transition-colors min-h-[200px]"
          >
            {preview ? (
              <img src={preview} alt="preview" className="max-h-48 rounded-lg object-contain" />
            ) : (
              <>
                <Upload size={32} className="text-steel-500" />
                <p className="text-steel-400 text-sm text-center">
                  Arrastra una imagen o toca para seleccionar
                </p>
              </>
            )}
          </div>
          <input ref={inputRef} type="file" accept="image/*" capture="environment"
            className="hidden" onChange={(e) => handleFile(e.target.files[0])} />

          <div className="flex gap-3">
            <button onClick={() => inputRef.current.click()}
              className="btn-ghost flex items-center gap-2 flex-1 justify-center">
              <Camera size={16} /> Cámara
            </button>
            <button onClick={handleAnalyze} disabled={!file || loading}
              className="btn-primary flex items-center gap-2 flex-1 justify-center">
              {loading
                ? <><Loader2 size={16} className="animate-spin" /> Analizando…</>
                : <><CheckCircle2 size={16} /> Analizar</>}
            </button>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-danger text-sm bg-danger/10 rounded-lg p-3">
              <XCircle size={16} /> {error}
            </div>
          )}
        </div>

        {/* ── Right — results ── */}
        <div className="space-y-4">
          {!result && !loading && (
            <div className="card flex flex-col items-center justify-center min-h-[300px] text-steel-500">
              <AlertTriangle size={32} className="mb-3" />
              <p className="text-sm">Los resultados aparecerán aquí</p>
            </div>
          )}

          {loading && (
            <div className="card flex flex-col items-center justify-center min-h-[300px]">
              <Loader2 size={36} className="animate-spin text-amber-400 mb-4" />
              <p className="text-steel-400 text-sm">Ejecutando YOLOv11…</p>
            </div>
          )}

          {result && !loading && (
            <>
              {/* Resumen general */}
              <div className="card">
                <div className="flex items-center justify-between mb-3">
                  <p className="font-semibold">Resultado</p>
                  <span className="badge bg-ok/10 text-ok border border-ok/30">
                    {result.inference_ms} ms
                  </span>
                </div>
                <p className="text-steel-300 text-sm">{result.analisis?.resumen}</p>
              </div>

              {/* Arrumes */}
              {result.analisis?.arrumes?.length > 0 && (
                <div className="space-y-3">
                  <p className="text-sm font-semibold text-steel-300 flex items-center gap-2">
                    <Layers size={15} className="text-amber-400" />
                    Arrumes detectados ({result.analisis.total_arrumes})
                  </p>
                  {result.analisis.arrumes.map((arr) => (
                    <div key={arr.arrume_id} className="card border-l-2 border-l-amber-400/50">
                      <div className="flex items-center justify-between mb-2">
                        <p className="font-semibold text-amber-400 text-sm">
                          Arrume {arr.arrume_id}
                        </p>
                        <span className="badge bg-amber-500/10 text-amber-400 border border-amber-500/30">
                          {arr.total_piezas} piezas
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {arr.familias.map((f) => (
                          <span key={f} className={`badge border ${FAMILY_COLOR[f] || "bg-steel-700 text-steel-300"}`}>
                            {f}
                          </span>
                        ))}
                      </div>
                      <p className="text-xs text-steel-500">
                        Confianza promedio: {arr.confianza_promedio}%
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Familias */}
              {result.analisis?.familias && Object.keys(result.analisis.familias).length > 0 && (
                <div className="card">
                  <p className="text-sm font-semibold text-steel-300 mb-3">Distribución por familia</p>
                  <div className="space-y-2">
                    {Object.entries(result.analisis.familias).map(([fam, count]) => (
                      <div key={fam} className="flex items-center gap-3">
                        <span className={`badge border w-14 justify-center ${FAMILY_COLOR[fam] || "bg-steel-700 text-steel-300"}`}>
                          {fam}
                        </span>
                        <div className="flex-1 bg-steel-900 rounded-full h-2">
                          <div
                            className="bg-amber-400 h-2 rounded-full transition-all"
                            style={{ width: `${(count / result.total_detected) * 100}%` }}
                          />
                        </div>
                        <span className="text-steel-300 text-sm font-semibold w-6 text-right">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Piezas individuales */}
              {result.pieces?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-steel-300">Piezas individuales</p>
                  {result.pieces.map((p, i) => (
                    <div key={i} className="card py-3">
                      <div className="flex items-center justify-between">
                        <p className="font-mono font-semibold text-amber-400 text-sm">{p.code}</p>
                        <span className={`font-mono text-sm font-semibold ${CONFIDENCE_COLOR(p.confidence)}`}>
                          {p.confidence}%
                        </span>
                      </div>
                      {p.known && p.specs && (
                        <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                          <Spec label="Largo" val={p.specs.largo_mm ? `${p.specs.largo_mm}mm` : "—"} />
                          <Spec label="Ancho" val={p.specs.ancho_mm ? `${p.specs.ancho_mm}mm` : "—"} />
                          <Spec label="Área"  val={p.specs.area_m2  ? `${p.specs.area_m2}m²`  : "—"} />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function Spec({ label, val }) {
  return (
    <div className="bg-steel-900/60 rounded p-1.5 text-center">
      <p className="text-steel-500 text-xs">{label}</p>
      <p className="text-steel-200 font-medium">{val}</p>
    </div>
  );
}
