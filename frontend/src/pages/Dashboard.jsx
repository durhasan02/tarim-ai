import { useQuery } from "@tanstack/react-query";
import { Map, Sprout, TrendingUp, AlertTriangle, CloudRain, CheckSquare } from "lucide-react";
import { dashboardApi } from "../api/dashboard";
import { useMe } from "../hooks/useAuth";

function StatCard({ label, value, unit, icon: Icon, color = "primary" }) {
  const colors = {
    primary: { bg: "bg-primary-50", text: "text-primary-700", icon: "text-primary-500" },
    blue: { bg: "bg-blue-50", text: "text-blue-700", icon: "text-blue-500" },
    orange: { bg: "bg-orange-50", text: "text-orange-700", icon: "text-orange-500" },
    green: { bg: "bg-green-50", text: "text-green-700", icon: "text-green-500" },
  };
  const c = colors[color];
  return (
    <div className={`card flex items-center gap-4 ${c.bg}`}>
      <div className={`p-3 rounded-lg bg-white shadow-sm ${c.icon}`}>
        <Icon size={22} />
      </div>
      <div>
        <p className="text-xs text-gray-500 mb-0.5">{label}</p>
        <p className={`text-2xl font-bold ${c.text}`}>
          {value ?? "—"} <span className="text-sm font-normal text-gray-400">{unit}</span>
        </p>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { data: user } = useMe();

  const { data: summary } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => dashboardApi.summary().then(r => r.data.data),
  });

  const { data: weather } = useQuery({
    queryKey: ["dashboard-weather"],
    queryFn: () => dashboardApi.weather(39.0, 35.0).then(r => r.data.data),
    staleTime: 1000 * 60 * 15,
  });

  const { data: tasks } = useQuery({
    queryKey: ["dashboard-tasks"],
    queryFn: () => dashboardApi.tasks().then(r => r.data.data),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Hoş geldiniz{user?.full_name ? `, ${user.full_name}` : ""}
        </p>
      </div>

      {/* Özet kartları */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Toplam Gelir" value={summary?.total_revenue?.toLocaleString("tr-TR")} unit="₺" icon={TrendingUp} color="primary" />
        <StatCard label="Toplam Tarla" value={summary?.total_fields} unit={`/ ${summary?.total_area_decare || 0} da`} icon={Map} color="green" />
        <StatCard label="Aktif Ekim" value={summary?.active_plantings} unit="parsel" icon={Sprout} color="blue" />
        <StatCard label="Kritik Stok" value={summary?.critical_stock_count} unit="kalem" icon={AlertTriangle} color="orange" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Hava durumu */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <CloudRain size={18} className="text-blue-500" />
            <h2 className="text-base font-semibold text-gray-900">
              Hava Durumu {weather?.city ? `— ${weather.city}` : ""}
            </h2>
          </div>

          {weather?.alerts?.length > 0 && (
            <div className="mb-3 space-y-1">
              {weather.alerts.map((a, i) => (
                <div key={i} className="bg-orange-50 border border-orange-200 rounded-lg px-3 py-2 text-sm text-orange-700 flex items-center gap-2">
                  <AlertTriangle size={14} /> {a.message}
                </div>
              ))}
            </div>
          )}

          <div className="space-y-2">
            {(weather?.forecasts || []).slice(0, 4).map((f, i) => (
              <div key={i} className="flex items-center justify-between py-1.5 border-b border-gray-100 last:border-0 text-sm">
                <span className="text-gray-500 w-36 truncate">{f.time}</span>
                <span className="font-medium">{f.temp}°C</span>
                <span className="text-blue-500">💧{f.humidity}%</span>
                <span className="text-gray-500">{f.rain_mm}mm</span>
                <span className="text-gray-400 text-xs">{f.description}</span>
              </div>
            ))}
            {!weather && <p className="text-sm text-gray-400">Hava durumu yükleniyor...</p>}
          </div>
        </div>

        {/* Yaklaşan görevler */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <CheckSquare size={18} className="text-primary-500" />
            <h2 className="text-base font-semibold text-gray-900">Yaklaşan Görevler</h2>
          </div>
          {tasks?.tasks?.length > 0 ? (
            <div className="space-y-2">
              {tasks.tasks.map((t, i) => (
                <div key={i} className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0">
                  <div className="w-2 h-2 rounded-full bg-primary-500 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{t.message}</p>
                    <p className="text-xs text-gray-500">{t.date}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-24 text-gray-400 text-sm">
              Bu hafta yaklaşan görev yok
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
