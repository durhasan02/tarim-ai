import { useState } from "react";
import { Link } from "react-router-dom";
import { useRegister } from "../hooks/useAuth";

export default function Register() {
  const { mutate: register, isPending } = useRegister();
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    phone: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    register(form);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-green-100">
      <div className="w-full max-w-md">
        <div className="card">
          <div className="text-center mb-8">
            <span className="text-5xl">🌾</span>
            <h1 className="mt-4 text-2xl font-bold text-gray-900">Hesap Oluştur</h1>
            <p className="mt-1 text-sm text-gray-500">Ücretsiz kayıt olun</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ad Soyad</label>
              <input
                type="text"
                className="input-field"
                placeholder="Ahmet Yılmaz"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">E-posta</label>
              <input
                type="email"
                required
                className="input-field"
                placeholder="ornek@mail.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
              <input
                type="tel"
                className="input-field"
                placeholder="0532 000 00 00"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Şifre <span className="text-gray-400 font-normal">(en az 8 karakter)</span>
              </label>
              <input
                type="password"
                required
                minLength={8}
                className="input-field"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>

            <button
              type="submit"
              disabled={isPending}
              className="btn-primary w-full mt-2"
            >
              {isPending ? "Kayıt olunuyor..." : "Kayıt Ol"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            Zaten hesabınız var mı?{" "}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              Giriş yapın
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
