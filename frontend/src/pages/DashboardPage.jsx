import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { apiFetch } from "../utils/api";

const COLORS = ["#f59e0b", "#3b82f6", "#a855f7", "#22c55e", "#ef4444", "#06b6d4"];

export default function DashboardPage() {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    apiFetch("/api/history/?limit=500").then((d) => setRecords(d.records)).catch(console.error);
  }, []);

  // KPIs
  const total        = records.length;
  const totalPieces  = records.reduce((s, r) => s + (r.total_detected || 0), 0);
  const avgMs        = total ? Math.round(records.reduce((s, r) => s + (r.inference_ms || 0), 0) / total) : 0;

  // Pieces by code
  const codeCount = {};
  records.forEach((r) =>
    (r.pieces || []).forEach((p) => {
      codeCount[p.code] = (codeCount[p.code] || 0) + 1;
    })
  );
  const pieData = Object.entries(codeCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);

  // Audits per day (last 14 days)
  const dayCounts = {};
  records.forEach((r) => {
    const day = r.timestamp?.slice(0, 10);
    if (day) dayCounts[day] = (dayCounts[day] || 0) + 1;
  });
  const barData = Object.entries(dayCounts)
    .sort()
    .slice(-14)
    .map(([date, count]) => ({ date: date.slice(5), count }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Indicadores KPI</h1>
        <p className="text-steel-400 text-sm mt-1">Basado en {total} auditorías registradas</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-3 gap-4">
        <KPI label="Auditorías" val={total} />
        <KPI label="Piezas detectadas" val={totalPieces} />
        <KPI label="Inferencia promedio" val={`${avgMs} ms`} />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Bar chart */}
        <div className="card">
          <p className="font-semibold mb-4 text-sm">Auditorías por día (últ. 14 días)</p>
          {barData.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barData}>
                <XAxis dataKey="date" tick={{ fill: "#627d98", fontSize: 11 }} />
                <YAxis tick={{ fill: "#627d98", fontSize: 11 }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#102a43", border: "1px solid #334e68" }} />
                <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-steel-500 text-sm text-center py-12">Sin datos</p>
          )}
        </div>

        {/* Pie chart */}
        <div className="card">
          <p className="font-semibold mb-4 text-sm">Distribución por código</p>
          {pieData.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={70} label>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#102a43", border: "1px solid #334e68" }} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#627d98" }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-steel-500 text-sm text-center py-12">Sin datos</p>
          )}
        </div>
      </div>

      {/* Power BI export note */}
      <div className="card border-amber-500/20 bg-amber-500/5 text-sm text-steel-300">
        <p className="font-semibold text-amber-400 mb-1">Exportar a Power BI</p>
        <p>
          El endpoint <span className="font-mono text-steel-200">/api/history/?limit=500</span> retorna
          JSON paginado directamente consumible por Power BI (conector Web). Actualización
          bajo demanda o programada.
        </p>
      </div>
    </div>
  );
}

function KPI({ label, val }) {
  return (
    <div className="card text-center">
      <p className="text-2xl font-bold text-amber-400">{val}</p>
      <p className="text-steel-400 text-xs mt-1">{label}</p>
    </div>
  );
}
