import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Map,
  Sprout,
  Droplets,
  HeartPulse,
  Wheat,
  LogOut,
} from "lucide-react";
import { useLogout } from "../../hooks/useAuth";
import { useAuthStore } from "../../store/authStore";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/fields", label: "Tarlalar", icon: Map },
  { to: "/plantings", label: "Ekim Planı", icon: Sprout },
  { to: "/irrigation", label: "Sulama", icon: Droplets },
  { to: "/health", label: "Bitki Sağlığı", icon: HeartPulse },
  { to: "/harvests", label: "Hasat & Satış", icon: Wheat },
];

export default function Sidebar() {
  const { mutate: logout } = useLogout();
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="w-64 flex flex-col bg-white border-r border-gray-200 h-full">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-gray-100">
        <span className="text-2xl">🌾</span>
        <span className="font-semibold text-gray-800 text-sm leading-tight">
          Tarım Yönetim<br />Sistemi
        </span>
      </div>

      {/* Navigasyon */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-primary-50 text-primary-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Kullanıcı & Çıkış */}
      <div className="px-3 py-4 border-t border-gray-100">
        {user && (
          <div className="px-3 py-2 text-xs text-gray-500 truncate mb-2">
            {user.full_name || user.email}
          </div>
        )}
        <button
          onClick={() => logout()}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <LogOut size={18} />
          Çıkış Yap
        </button>
      </div>
    </aside>
  );
}
