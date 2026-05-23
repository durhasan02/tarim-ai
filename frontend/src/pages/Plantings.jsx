import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Plus, Sprout, CheckCircle, XCircle } from "lucide-react";
import { plantingsApi } from "../api/plantings";
import { fieldsApi } from "../api/fields";

const CROP_TYPES = ["Buğday", "Mısır", "Domates", "Patates", "Biber", "Pamuk", "Ayçiçeği", "Arpa", "Çeltik", "Soğan"];
const STATUS_LABELS = { active: "Aktif", harvested: "Hasat edildi", failed: "Başarısız" };
const STATUS_COLORS = { active: "bg-green-100 text-green-700", harvested: "bg-blue-100 text-blue-700", failed: "bg-red-100 text-red-700" };

function PlantingForm({ fields, onSubmit, loading, onCancel }) {
  const [form, setForm] = useState({
    field_id: "", crop_type: "", planting_date: "", expected_harvest_date: "", seed_amount: "", seed_unit: "kg", notes: "",
  });
  return (
    <div className="card space-y-3">
      <h3 className="text-sm font-semibold text-gray-900">Yeni Ekim Planı</h3>
      <select className="input-field" value={form.field_id} onChange={(e) => setForm({ ...form, field_id: e.target.value })}>
        <option value="">Tarla seçin *</option>
        {fields.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
      </select>
      <select className="input-field" value={form.crop_type} onChange={(e) => setForm({ ...form, crop_type: e.target.value })}>
        <option value="">Ürün seçin *</option>
        {CROP_TYPES.map(c => <option key={c} value={c}>{c}</option>)}
      </select>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Ekim tarihi *</label>
          <input type="date" className="input-field" value={form.planting_date}
            onChange={(e) => setForm({ ...form, planting_date: e.target.value })} />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Tahmini hasat</label>
          <input type="date" className="input-field" value={form.expected_harvest_date}
            onChange={(e) => setForm({ ...form, expected_harvest_date: e.target.value })} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <input type="number" className="input-field" placeholder="Tohum miktarı"
          value={form.seed_amount} onChange={(e) => setForm({ ...form, seed_amount: e.target.value })} />
        <select className="input-field" value={form.seed_unit} onChange={(e) => setForm({ ...form, seed_unit: e.target.value })}>
          <option value="kg">kg</option>
          <option value="adet">adet</option>
        </select>
      </div>
      <textarea className="input-field" rows={2} placeholder="Notlar"
        value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
      <div className="flex gap-2">
        <button className="btn-primary flex-1" disabled={loading || !form.field_id || !form.crop_type || !form.planting_date}
          onClick={() => onSubmit({
            ...form,
            seed_amount: form.seed_amount ? parseFloat(form.seed_amount) : null,
            expected_harvest_date: form.expected_harvest_date || null,
          })}>
          {loading ? "Kaydediliyor..." : "Kaydet"}
        </button>
        <button className="btn-secondary" onClick={onCancel}>İptal</button>
      </div>
    </div>
  );
}

export default function Plantings() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);

  const { data: plantings = [], isLoading } = useQuery({
    queryKey: ["plantings"],
    queryFn: () => plantingsApi.list().then(r => r.data.data),
  });

  const { data: fields = [] } = useQuery({
    queryKey: ["fields"],
    queryFn: () => fieldsApi.list().then(r => r.data.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => plantingsApi.create(data),
    onSuccess: () => {
      toast.success("Ekim planı eklendi");
      qc.invalidateQueries({ queryKey: ["plantings"] });
      setShowForm(false);
    },
    onError: () => toast.error("Ekim planı eklenemedi"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => plantingsApi.update(id, data),
    onSuccess: () => { toast.success("Güncellendi"); qc.invalidateQueries({ queryKey: ["plantings"] }); },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Ekim Planlaması</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(true)}>
          <Plus size={16} /> Yeni Ekim
        </button>
      </div>

      {showForm && (
        <PlantingForm fields={fields} onSubmit={(d) => createMutation.mutate(d)}
          loading={createMutation.isPending} onCancel={() => setShowForm(false)} />
      )}

      {isLoading ? (
        <div className="text-center text-gray-400 py-8">Yükleniyor...</div>
      ) : plantings.length === 0 ? (
        <div className="card flex flex-col items-center py-12 text-gray-400">
          <Sprout size={40} className="mb-3" />
          <p>Henüz ekim planı yok</p>
          <p className="text-sm mt-1">Önce tarla ekleyin, sonra ekim planlayın</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {plantings.map((p) => {
            const field = fields.find(f => f.id === p.field_id);
            return (
              <div key={p.id} className="card space-y-2">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{p.crop_type}</p>
                    <p className="text-xs text-gray-500">{field?.name || "Tarla"}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[p.status]}`}>
                    {STATUS_LABELS[p.status]}
                  </span>
                </div>
                <div className="text-xs text-gray-500 space-y-1">
                  <p>Ekim: {p.planting_date}</p>
                  {p.expected_harvest_date && <p>Tahmini hasat: {p.expected_harvest_date}</p>}
                  {p.seed_amount && <p>Tohum: {p.seed_amount} {p.seed_unit}</p>}
                </div>
                {p.status === "active" && (
                  <div className="flex gap-2 pt-1">
                    <button
                      className="text-xs text-green-600 hover:underline flex items-center gap-1"
                      onClick={() => updateMutation.mutate({ id: p.id, data: { status: "harvested" } })}
                    >
                      <CheckCircle size={12} /> Hasat edildi
                    </button>
                    <button
                      className="text-xs text-red-500 hover:underline flex items-center gap-1"
                      onClick={() => updateMutation.mutate({ id: p.id, data: { status: "failed" } })}
                    >
                      <XCircle size={12} /> Başarısız
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
