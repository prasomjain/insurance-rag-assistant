import { Activity, BarChart3 } from "lucide-react";
import { NavLink, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { ChatPage } from "./pages/ChatPage";

function App() {
  const navClass = ({ isActive }: { isActive: boolean }) =>
    `inline-flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-all ${
      isActive ?
        "bg-cyan-600/30 text-cyan-200 border-cyan-500/60"
      : "bg-slate-900/40 text-slate-300 border-slate-700 hover:border-cyan-500/40 hover:text-cyan-300"
    }`;

  return (
    <div className="min-h-screen bg-slate-950">
      <nav className="sticky top-0 z-40 border-b border-white/10 backdrop-blur-xl bg-slate-950/80">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
          <NavLink to="/" end className={navClass}>
            <Activity className="w-4 h-4" />
            Chat Assistant
          </NavLink>
          <NavLink to="/dashboard" className={navClass}>
            <BarChart3 className="w-4 h-4" />
            Evaluation Dashboard
          </NavLink>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </div>
  );
}

export default App;
