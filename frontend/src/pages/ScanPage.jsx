import { useState, useRef, useCallback } from "react";
import { Upload, Camera, Loader2, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { detectPiece } from "../utils/api";

const CONFIDENCE_COLOR = (c) =>
  c >= 80 ? "text-ok" : c >= 60 ? "text-amber-400" : "text-danger";

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
    const url = URL.createObjectURL(f);
    setPreview(url);
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
      // Guardar en historial
      await fetch("/api/history/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operator_id: operator,
          image_file: data.image_file,
          inference_ms: data.inference_ms,
          total_detected: data.total_detected,
          pieces: data.pieces,
        }),
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Escaneo IA</h1>
        <p className="text-steel-400 text-sm mt-1">
          Captura o sube una foto de la pieza — YOLOv8 la identificará automáticamente.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left — upload */}
        <div className="space-y-4">
          <div>
            <label className="text-sm text-steel-400 mb-1 block">Operador</label>
            <select
              value={operator}
              onChange={(e) => setOperator(e.target.value)}
              className="input"
            >
              <option value="OP-001">OP-001 — Carlos Ramírez</option>
              <option value="OP-002">OP-002 — Ana Torres</option>
              <option value="OP-003">OP-003 — Luis Mendez</option>
            </select>
          </div>

          {/* Drop zone */}
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
                  Arrastra una imagen o haz clic para seleccionar
                </p>
                <p className="text-steel-600 text-xs">PNG · JPG · WEBP · máx. 16 MB</p>
              </>
            )}
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => handleFile(e.target.files[0])}
          />

          <div className="flex gap-3">
            <button
              onClick={() => inputRef.current.click()}
              className="btn-ghost flex items-center gap-2 flex-1 justify-center"
            >
              <Camera size={16} /> Cámara
            </button>
            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="btn-primary flex items-center gap-2 flex-1 justify-center"
            >
              {loading ? (
                <><Loader2 size={16} className="animate-spin" /> Analizando…</>
              ) : (
                <><CheckCircle2 size={16} /> Analizar</>
              )}
            </button>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-danger text-sm bg-danger/10 rounded-lg p-3">
              <XCircle size={16} /> {error}
            </div>
          )}
        </div>

        {/* Right — results */}
        <div>
          {!result && !loading && (
            <div className="card flex flex-col items-center justify-center min-h-[300px] text-steel-500">
              <AlertTriangle size={32} className="mb-3" />
              <p className="text-sm">Los resultados aparecerán aquí</p>
            </div>
          )}

          {loading && (
            <div className="card flex flex-col items-center justify-center min-h-[300px]">
              <Loader2 size={36} className="animate-spin text-amber-400 mb-4" />
              <p className="text-steel-400 text-sm">Ejecutando inferencia YOLOv8…</p>
            </div>
          )}

          {result && !loading && (
            <div className="space-y-4">
              <div className="card">
                <div className="flex items-center justify-between mb-3">
                  <p className="font-semibold">Resultado</p>
                  <span className="badge bg-ok/10 text-ok border border-ok/30">
                    {result.inference_ms} ms
                  </span>
                </div>
                <p className="text-steel-400 text-sm">
                  {result.total_detected} pieza(s) detectada(s)
                </p>
              </div>

              {result.pieces.map((p, i) => (
                <div key={i} className="card space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="font-mono font-semibold text-amber-400">{p.code}</p>
                    <span className={`font-mono text-sm font-semibold ${CONFIDENCE_COLOR(p.confidence)}`}>
                      {p.confidence}%
                    </span>
                  </div>

                  {p.known ? (
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <Spec label="Familia"   val={p.specs.family} />
                      <Spec label="Largo"     val={`${p.specs.largo_cm} cm`} />
                      <Spec label="Ancho"     val={`${p.specs.ancho_cm} cm`} />
                      <Spec label="Refuerzos" val={p.specs.refuerzos} />
                      <div className="col-span-2">
                        <Spec label="Material" val={p.specs.material} />
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-steel-500">
                      Clase no mapeada en catálogo UNISPAN
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Spec({ label, val }) {
  return (
    <div>
      <p className="text-steel-500 text-xs">{label}</p>
      <p className="text-steel-100 font-medium">{val}</p>
    </div>
  );
}
