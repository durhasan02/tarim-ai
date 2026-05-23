import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { lazy, Suspense } from "react";
import Layout from "./components/layout/Layout";
import { useAuthStore } from "./store/authStore";

const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Fields = lazy(() => import("./pages/Fields"));
const Plantings = lazy(() => import("./pages/Plantings"));
const Irrigation = lazy(() => import("./pages/Irrigation"));
const HealthCheck = lazy(() => import("./pages/HealthCheck"));
const Harvests = lazy(() => import("./pages/Harvests"));

function RequireAuth({ children }) {
  const isAuthenticated = useAuthStore((s) => !!s.accessToken);
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function GuestOnly({ children }) {
  const isAuthenticated = useAuthStore((s) => !!s.accessToken);
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

function PageLoader() {
  return (
    <div className="flex items-center justify-center h-full min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<GuestOnly><Login /></GuestOnly>} />
          <Route path="/register" element={<GuestOnly><Register /></GuestOnly>} />

          {/* Protected */}
          <Route path="/" element={<RequireAuth><Layout /></RequireAuth>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="fields" element={<Fields />} />
            <Route path="plantings" element={<Plantings />} />
            <Route path="irrigation" element={<Irrigation />} />
            <Route path="health" element={<HealthCheck />} />
            <Route path="harvests" element={<Harvests />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
