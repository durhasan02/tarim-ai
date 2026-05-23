import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Plus, Wheat, TrendingUp } from "lucide-react";
import { harvestsApi } from "../api/harvests";
import { fieldsApi } from "../api/fields";
import { plantingsApi } from "../api/plantings";

function HarvestForm({ fields, plantings, onSubmit, loading, onCancel }) {
  const [form, setForm] = useState({ planting_id: "", field_id: "", harvest_date: "", total_amount: "", unit: "kg", quality_grade: "", notes: "" });

  const selectedPlanting = plantings.find(p => p.id === form.planting_id);

  return (
    <div className="card space-y-3">
      <h3 className="text-sm font-semibold text-gray-900">Hasat Kaydı</h3>
      <select className="input-field" value={form.planting_id}
        onChange={(e) => {
          const p = plantings.find(x => x.id === e.target.value);
          setForm({ ...form, planting_id: e.target.value, field_id: p?.field_id || "" });
        }}>
        <option value="">Ekim seçin *</option>
        {plantings.filter(p => p.status === "active").map(p => (
          <option key={p.id} value={p.id}>{p.crop_type} — {fields.find(f => f.id === p.field_id)?.name}</option>
        ))}
      </select>
      <input type="date" className="input-field" value={form.harvest_date}
        onChange={(e) => setForm({ ...form, harvest_date: e.target.value })} />
      <div className="grid grid-cols-2 gap-2">
        <input type="number" className="input-field" placeholder="Miktar *"
          value={form.total_amount} onChange={(e) => setForm({ ...form, total_amount: e.target.value })} />
        <select className="input-field" value={form.unit}
          onChange={(e) => setForm({ ...form, unit: e.target.value })}>
          <option value="kg">kg</option>
          <option value="ton">ton</option>
          <option value="adet">adet</option>
        </select>
      </div>
      <select className="input-field" value={form.quality_grade}
        onChange={(e) => setForm({ ...form, quality_grade: e.target.value })}>
        <option value="">Kalite sınıfı</option>
        <option value="A">A — Birinci</option>
        <option value="B">B — İkinci</option>
        <option value="C">C — Üçüncü</option>
      </select>
      <div className="flex gap-2">
        <button className="btn-primary flex-1"
          disabled={loading || !form.planting_id || !form.harvest_date || !form.total_amount}
          onClick={() => onSubmit({ ...form, total_amount: parseFloat(form.total_amount) })}>
          {loading ? "Kaydediliyor..." : "Kaydet"}
        </button>
        <button className="btn-secondary" onClick={onCancel}>İptal</button>
      </div>
    </div>
  );
}

function SaleForm({ harvests, onSubmit, loading, onCancel }) {
  const [form, setForm] = useState({ harvest_id: "", sale_date: "", amount: "", unit: "kg", unit_price: "", buyer_name: "" });
  return (
    <div className="card space-y-3">
      <h3 className="text-sm font-semibold text-gray-900">Satış Kaydı</h3>
      <select className="input-field" value={form.harvest_id}
        onChange={(e) => setForm({ ...form, harvest_id: e.target.value })}>
        <option value="">Hasat seçin *</option>
        {harvests.map(h => <option key={h.id} value={h.id}>{h.harvest_date} — {h.total_amount} {h.unit}</option>)}
      </select>
      <input type="date" className="input-field" value={form.sale_date}
        onChange={(e) => setForm({ ...form, sale_date: e.target.value })} />
      <div className="grid grid-cols-2 gap-2">
        <input type="number" className="input-field" placeholder="Satılan miktar *"
          value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        <input type="number" className="input-field" placeholder="Birim fiyat (₺)"
          value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} />
      </div>
      <input className="input-field" placeholder="Alıcı adı"
        value={form.buyer_name} onChange={(e) => setForm({ ...form, buyer_name: e.target.value })} />
      {form.amount && form.unit_price && (
        <div className="bg-primary-50 rounded-lg px-3 py-2 text-sm text-primary-700 font-medium">
          Toplam gelir: {(parseFloat(form.amount) * parseFloat(form.unit_price)).toLocaleString("tr-TR")} ₺
        </div>
      )}
      <div className="flex gap-2">
        <button className="btn-primary flex-1"
          disabled={loading || !form.harvest_id || !form.sale_date || !form.amount}
          onClick={() => onSubmit({ ...form, amount: parseFloat(form.amount), unit_price: form.unit_price ? parseFloat(form.unit_price) : null })}>
          {loading ? "Kaydediliyor..." : "Kaydet"}
        </button>
        <button className="btn-secondary" onClick={onCancel}>İptal</button>
      </div>
    </div>
  );
}

export default function Harvests() {
  const qc = useQueryClient();
  const [showHarvestForm, setShowHarvestForm] = useState(false);
  const [showSaleForm, setShowSaleForm] = useState(false);

  const { data: harvests = [], isLoading } = useQuery({
    queryKey: ["harvests"],
    queryFn: () => harvestsApi.list().then(r => r.data.data),
  });
  const { data: fields = [] } = useQuery({ queryKey: ["fields"], queryFn: () => fieldsApi.list().then(r => r.data.data) });
  const { data: plantings = [] } = useQuery({ queryKey: ["plantings"], queryFn: () => plantingsApi.list().then(r => r.data.data) });
  const { data: summary } = useQuery({ queryKey: ["sales-summary"], queryFn: () => harvestsApi.salesSummary().then(r => r.data.data) });

  const harvestMutation = useMutation({
    mutationFn: (data) => harvestsApi.create(data),
    onSuccess: () => { toast.success("Hasat kaydedildi"); qc.invalidateQueries({ queryKey: ["harvests"] }); setShowHarvestForm(false); },
    onError: () => toast.error("Hata oluştu"),
  });

  const saleMutation = useMutation({
    mutationFn: (data) => harvestsApi.createSale(data),
    onSuccess: () => { toast.success("Satış kaydedildi"); qc.invalidateQueries({ queryKey: ["sales-summary"] }); setShowSaleForm(false); },
    onError: () => toast.error("Hata oluştu"),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Hasat & Satış</h1>
        <div className="flex gap-2">
          <button className="btn-secondary flex items-center gap-2" onClick={() => setShowSaleForm(true)}>
            <TrendingUp size={16} /> Satış Ekle
          </button>
          <button className="btn-primary flex items-center gap-2" onClick={() => setShowHarvestForm(true)}>
            <Plus size={16} /> Hasat Kaydet
          </button>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 gap-4">
          <div className="card">
            <div className="text-xs text-gray-500 mb-1">Toplam Gelir</div>
            <div className="text-2xl font-bold text-primary-700">
              {summary.total_revenue.toLocaleString("tr-TR")} ₺
            </div>
          </div>
          <div className="card">
            <div className="text-xs text-gray-500 mb-1">Toplam Satış</div>
            <div className="text-2xl font-bold text-gray-900">{summary.total_sales}</div>
          </div>
        </div>
      )}

      {showHarvestForm && (
        <HarvestForm fields={fields} plantings={plantings}
          onSubmit={(d) => harvestMutation.mutate(d)}
          loading={harvestMutation.isPending} onCancel={() => setShowHarvestForm(false)} />
      )}
      {showSaleForm && (
        <SaleForm harvests={harvests}
          onSubmit={(d) => saleMutation.mutate(d)}
          loading={saleMutation.isPending} onCancel={() => setShowSaleForm(false)} />
      )}

      {isLoading ? (
        <div className="text-center text-gray-400 py-8">Yükleniyor...</div>
      ) : harvests.length === 0 ? (
        <div className="card flex flex-col items-center py-12 text-gray-400">
          <Wheat size={40} className="mb-3" />
          <p>Henüz hasat kaydı yok</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 text-gray-500 font-medium">Tarih</th>
                <th className="text-left py-2 px-3 text-gray-500 font-medium">Miktar</th>
                <th className="text-left py-2 px-3 text-gray-500 font-medium">Verim (da)</th>
                <th className="text-left py-2 px-3 text-gray-500 font-medium">Kalite</th>
              </tr>
            </thead>
            <tbody>
              {harvests.map((h) => (
                <tr key={h.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-2 px-3">{h.harvest_date}</td>
                  <td className="py-2 px-3 font-medium">{h.total_amount} {h.unit}</td>
                  <td className="py-2 px-3">{h.yield_per_decare || "—"}</td>
                  <td className="py-2 px-3">
                    {h.quality_grade ? (
                      <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs">{h.quality_grade}</span>
                    ) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
