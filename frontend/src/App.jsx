import { useState } from "react";
import { ScanLine, BookOpen, Clock, BarChart2, Users } from "lucide-react";
import ScanPage from "./pages/ScanPage";
import CatalogPage from "./pages/CatalogPage";
import HistoryPage from "./pages/HistoryPage";
import DashboardPage from "./pages/DashboardPage";
import OperatorsPage from "./pages/OperatorsPage";

const TABS = [
  { id: "scan",       label: "Escaneo IA",   Icon: ScanLine  },
  { id: "catalog",    label: "Catálogo",      Icon: BookOpen  },
  { id: "history",    label: "Historial",     Icon: Clock     },
  { id: "dashboard",  label: "Indicadores",   Icon: BarChart2 },
  { id: "operators",  label: "Operadores",    Icon: Users     },
];

export default function App() {
  const [tab, setTab] = useState("scan");

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-steel-600/40 bg-steel-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-md bg-amber-500 flex items-center justify-center">
            <span className="text-steel-900 font-bold text-sm">U</span>
          </div>
          <div>
            <p className="font-semibold text-steel-100 leading-none">Auditoría UNISPAN IA</p>
            <p className="text-xs text-steel-400">Control de formaletas metálicas</p>
          </div>
          <div className="ml-auto">
            <span className="badge bg-ok/10 text-ok border border-ok/30">Sistema activo</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="max-w-6xl mx-auto px-4 flex gap-1 pb-0 overflow-x-auto">
          {TABS.map(({ id, label, Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
                ${tab === id
                  ? "border-amber-400 text-amber-400"
                  : "border-transparent text-steel-400 hover:text-steel-200"
                }`}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        {tab === "scan"      && <ScanPage />}
        {tab === "catalog"   && <CatalogPage />}
        {tab === "history"   && <HistoryPage />}
        {tab === "dashboard" && <DashboardPage />}
        {tab === "operators" && <OperatorsPage />}
      </main>
    </div>
  );
}
