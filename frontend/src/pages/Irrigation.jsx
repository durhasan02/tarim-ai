import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Plus, Droplets, AlertTriangle, Cpu, Loader2 } from "lucide-react";
import { stockApi } from "../api/stock";
import { aiApi } from "../api/ai";
import { fieldsApi } from "../api/fields";

const CATEGORIES = ["fertilizer", "pesticide", "herbicide", "equipment"];
const CAT_LABELS = { fertilizer: "Gübre", pesticide: "İlaç", herbicide: "Herbisit", equipment: "Ekipman" };
const CAT_COLORS = { fertilizer: "bg-green-100 text-green-700", pesticide: "bg-yellow-100 text-yellow-700", herbicide: "bg-orange-100 text-orange-700", equipment: "bg-blue-100 text-blue-700" };

function StockForm({ onSubmit, loading, onCancel }) {
  const [form, setForm] = useState({ name: "", category: "", quantity: "", unit: "kg", critical_level: "", purchase_price: "" });
  return (
    <div className="card space-y-3">
      <h3 className="text-sm font-semibold text-gray-900">Yeni Stok Kalemi</h3>
      <input className="input-field" placeholder="Ad *" value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })} />
      <div className="grid grid-cols-2 gap-2">
        <select className="input-field" value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}>
          <option value="">Kategori</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{CAT_LABELS[c]}</option>)}
        </select>
        <select className="input-field" value={form.unit}
          onChange={(e) => setForm({ ...form, unit: e.target.value })}>
          <option value="kg">kg</option>
          <option value="lt">lt</option>
          <option value="adet">adet</option>
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <input type="number" className="input-field" placeholder="Miktar *"
          value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
        <input type="number" className="input-field" placeholder="Kritik seviye"
          value={form.critical_level} onChange={(e) => setForm({ ...form, critical_level: e.target.value })} />
      </div>
      <input type="number" className="input-field" placeholder="Alış fiyatı (₺)"
        value={form.purchase_price} onChange={(e) => setForm({ ...form, purchase_price: e.target.value })} />
      <div className="flex gap-2">
        <button className="btn-primary flex-1"
          disabled={loading || !form.name || !form.quantity}
          onClick={() => onSubmit({
            ...form,
            quantity: parseFloat(form.quantity),
            critical_level: form.critical_level ? parseFloat(form.critical_level) : null,
            purchase_price: form.purchase_price ? parseFloat(form.purchase_price) : null,
          })}>
          {loading ? "Kaydediliyor..." : "Kaydet"}
        </button>
        <button className="btn-secondary" onClick={onCancel}>İptal</button>
      </div>
    </div>
  );
}

function MoveModal({ item, onClose }) {
  const qc = useQueryClient();
  const [form, setForm] = useState({ movement_type: "out", quantity: "", reason: "use" });

  const moveMutation = useMutation({
    mutationFn: (data) => stockApi.move(item.id, data),
    onSuccess: () => { toast.success("Stok güncellendi"); qc.invalidateQueries({ queryKey: ["stock"] }); onClose(); },
    onError: () => toast.error("Hata oluştu"),
  });

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-sm space-y-3 shadow-xl">
        <h3 className="font-semibold text-gray-900">Stok Hareketi — {item.name}</h3>
        <p className="text-sm text-gray-500">Mevcut: {item.quantity} {item.unit}</p>
        <select className="input-field" value={form.movement_type}
          onChange={(e) => setForm({ ...form, movement_type: e.target.value })}>
          <option value="out">Kullanım (çıkış)</option>
          <option value="in">Satın alma (giriş)</option>
        </select>
        <input type="number" className="input-field" placeholder="Miktar *"
          value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
        <select className="input-field" value={form.reason}
          onChange={(e) => setForm({ ...form, reason: e.target.value })}>
          <option value="use">Kullanım</option>
          <option value="purchase">Satın alma</option>
          <option value="waste">Fire</option>
        </select>
        <div className="flex gap-2">
          <button className="btn-primary flex-1"
            disabled={moveMutation.isPending || !form.quantity}
            onClick={() => moveMutation.mutate({ ...form, quantity: parseFloat(form.quantity) })}>
            Kaydet
          </button>
          <button className="btn-secondary" onClick={onClose}>İptal</button>
        </div>
      </div>
    </div>
  );
}

function IrrigationAI() {
  const { data: fields = [] } = useQuery({ queryKey: ["fields"], queryFn: () => fieldsApi.list().then(r => r.data.data) });
  const [selectedField, setSelectedField] = useState("");
  const [result, setResult] = useState(null);

  const { mutate, isPending } = useMutation({
    mutationFn: () => aiApi.irrigationRecommendation(selectedField),
    onSuccess: (res) => setResult(res.data.data),
    onError: (err) => toast.error(err.response?.data?.detail || "AI servisi erişilemiyor"),
  });

  const WHEN_COLORS = { now: "text-red-600", today: "text-orange-600", delay_24h: "text-blue-600", not_needed: "text-green-600" };

  return (
    <div className="card space-y-3">
      <div className="flex items-center gap-2 text-primary-700 font-semibold text-sm">
        <Cpu size={16} /> AI Sulama Önerisi
      </div>
      <div className="flex gap-2">
        <select className="input-field flex-1" value={selectedField} onChange={(e) => { setSelectedField(e.target.value); setResult(null); }}>
          <option value="">Tarla seçin</option>
          {fields.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
        </select>
        <button className="btn-primary flex items-center gap-1" disabled={!selectedField || isPending} onClick={() => mutate()}>
          {isPending ? <Loader2 size={14} className="animate-spin" /> : <Cpu size={14} />}
          Hesapla
        </button>
      </div>
      {result && (
        <div className="bg-primary-50 rounded-lg p-3 space-y-1">
          <p className="text-2xl font-bold text-primary-700">
            {result.water_amount_liters_per_decare} <span className="text-sm font-normal text-gray-500">lt/dekar</span>
          </p>
          <p className={`text-sm font-medium ${WHEN_COLORS[result.when] || "text-gray-700"}`}>{result.timing}</p>
          <p className="text-xs text-gray-500">{result.reason}</p>
          <p className="text-xs text-gray-400">Gelişim aşaması: {result.growth_stage} · Model: {result.model_used}</p>
        </div>
      )}
    </div>
  );
}

export default function Irrigation() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [moveItem, setMoveItem] = useState(null);

  const { data: stock = [], isLoading } = useQuery({
    queryKey: ["stock"],
    queryFn: () => stockApi.list().then(r => r.data.data),
  });

  const { data: alerts = [] } = useQuery({
    queryKey: ["stock-alerts"],
    queryFn: () => stockApi.alerts().then(r => r.data.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => stockApi.create(data),
    onSuccess: () => { toast.success("Stok kalemi eklendi"); qc.invalidateQueries({ queryKey: ["stock"] }); setShowForm(false); },
    onError: () => toast.error("Eklenemedi"),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Sulama & Stok</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(true)}>
          <Plus size={16} /> Stok Ekle
        </button>
      </div>

      {alerts.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2 text-orange-700 font-medium text-sm">
            <AlertTriangle size={16} /> {alerts.length} kalem kritik seviyenin altında
          </div>
          {alerts.map(a => (
            <p key={a.id} className="text-sm text-orange-600">
              · {a.name}: {a.quantity} {a.unit} (kritik: {a.critical_level} {a.unit})
            </p>
          ))}
        </div>
      )}

      <IrrigationAI />

      {showForm && (
        <StockForm onSubmit={(d) => createMutation.mutate(d)}
          loading={createMutation.isPending} onCancel={() => setShowForm(false)} />
      )}

      {moveItem && <MoveModal item={moveItem} onClose={() => setMoveItem(null)} />}

      {isLoading ? (
        <div className="text-center text-gray-400 py-8">Yükleniyor...</div>
      ) : stock.length === 0 ? (
        <div className="card flex flex-col items-center py-12 text-gray-400">
          <Droplets size={40} className="mb-3" />
          <p>Stok kaydı yok</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {stock.map((item) => (
            <div key={item.id} className={`card space-y-2 ${item.is_critical ? "border-orange-300 bg-orange-50" : ""}`}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-gray-900">{item.name}</p>
                  {item.category && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${CAT_COLORS[item.category] || "bg-gray-100 text-gray-600"}`}>
                      {CAT_LABELS[item.category] || item.category}
                    </span>
                  )}
                </div>
                {item.is_critical && <AlertTriangle size={16} className="text-orange-500 flex-shrink-0" />}
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {item.quantity} <span className="text-sm font-normal text-gray-500">{item.unit}</span>
              </div>
              {item.critical_level && (
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${item.is_critical ? "bg-orange-500" : "bg-primary-500"}`}
                    style={{ width: `${Math.min(100, (item.quantity / (item.critical_level * 3)) * 100)}%` }}
                  />
                </div>
              )}
              <button className="text-xs text-primary-600 hover:underline"
                onClick={() => setMoveItem(item)}>
                Stok hareketi ekle
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
