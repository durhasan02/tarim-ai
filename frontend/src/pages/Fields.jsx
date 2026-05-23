import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MapContainer, TileLayer, Polygon, Tooltip } from "react-leaflet";
import DrawControl from "../components/map/DrawControl";
import toast from "react-hot-toast";
import { Trash2, Map } from "lucide-react";
import { fieldsApi } from "../api/fields";
import "leaflet/dist/leaflet.css";

const SOIL_TYPES = ["clay", "sandy", "loamy", "silty"];
const IRRIGATION_SOURCES = ["rain", "drip", "sprinkler", "flood"];
const SOIL_LABELS = { clay: "Killi", sandy: "Kumlu", loamy: "Tınlı", silty: "Siltli" };
const IRRIG_LABELS = { rain: "Yağmur", drip: "Damla", sprinkler: "Yağmurlama", flood: "Taşkın" };

function FieldForm({ onSubmit, loading }) {
  const [form, setForm] = useState({ name: "", soil_type: "", irrigation_source: "", notes: "" });
  return (
    <div className="space-y-3">
      <input className="input-field" placeholder="Tarla adı *" value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })} />
      <select className="input-field" value={form.soil_type}
        onChange={(e) => setForm({ ...form, soil_type: e.target.value })}>
        <option value="">Toprak tipi seçin</option>
        {SOIL_TYPES.map(t => <option key={t} value={t}>{SOIL_LABELS[t]}</option>)}
      </select>
      <select className="input-field" value={form.irrigation_source}
        onChange={(e) => setForm({ ...form, irrigation_source: e.target.value })}>
        <option value="">Sulama kaynağı seçin</option>
        {IRRIGATION_SOURCES.map(s => <option key={s} value={s}>{IRRIG_LABELS[s]}</option>)}
      </select>
      <textarea className="input-field" rows={2} placeholder="Notlar"
        value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
      <button className="btn-primary w-full" disabled={loading || !form.name}
        onClick={() => onSubmit(form)}>
        {loading ? "Kaydediliyor..." : "Tarla Kaydet"}
      </button>
    </div>
  );
}

export default function Fields() {
  const qc = useQueryClient();
  const [drawnGeometry, setDrawnGeometry] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["fields"],
    queryFn: () => fieldsApi.list().then(r => r.data.data),
  });

  const createMutation = useMutation({
    mutationFn: (formData) => fieldsApi.create({ ...formData, geometry: drawnGeometry }),
    onSuccess: () => {
      toast.success("Tarla eklendi");
      qc.invalidateQueries({ queryKey: ["fields"] });
      setDrawnGeometry(null);
      setShowForm(false);
    },
    onError: () => toast.error("Tarla eklenemedi"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => fieldsApi.delete(id),
    onSuccess: () => { toast.success("Tarla silindi"); qc.invalidateQueries({ queryKey: ["fields"] }); },
  });

  const handleCreated = (e) => {
    const layer = e.layer;
    const geojson = layer.toGeoJSON();
    setDrawnGeometry(geojson.geometry);
    setShowForm(true);
    toast.success("Tarla çizildi! Formu doldurup kaydedin.");
  };

  const fields = data || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Tarlalar & Parseller</h1>
        <span className="text-sm text-gray-500">{fields.length} tarla</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Harita */}
        <div className="lg:col-span-2 card p-0 overflow-hidden" style={{ height: 480 }}>
          <MapContainer
            center={[39.0, 35.0]}
            zoom={6}
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="© OpenStreetMap"
            />
            <DrawControl onCreated={handleCreated} />
            <>
              {fields.map((f) => (
                f.geometry?.coordinates && (
                  <Polygon
                    key={f.id}
                    positions={f.geometry.coordinates[0].map(([lng, lat]) => [lat, lng])}
                    pathOptions={{ color: "#16a34a", fillOpacity: 0.3 }}
                  >
                    <Tooltip>{f.name} ({f.area_decare} da)</Tooltip>
                  </Polygon>
                )
              ))}
            </>
          </MapContainer>
        </div>

        {/* Sağ panel */}
        <div className="space-y-3">
          {showForm && drawnGeometry && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Yeni Tarla</h3>
              <FieldForm onSubmit={(form) => createMutation.mutate(form)} loading={createMutation.isPending} />
            </div>
          )}

          {!showForm && (
            <div className="card flex flex-col items-center justify-center py-8 text-center text-gray-400">
              <Map size={32} className="mb-2" />
              <p className="text-sm">Haritada polygon aracıyla tarla çizin</p>
            </div>
          )}

          {/* Tarla listesi */}
          {isLoading ? (
            <div className="text-center text-sm text-gray-400">Yükleniyor...</div>
          ) : (
            fields.map((f) => (
              <div key={f.id} className="card py-3 px-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{f.name}</p>
                  <p className="text-xs text-gray-500">
                    {f.area_decare ? `${f.area_decare} da` : "Alan hesaplanmadı"}
                    {f.soil_type ? ` · ${SOIL_LABELS[f.soil_type] || f.soil_type}` : ""}
                  </p>
                </div>
                <button onClick={() => deleteMutation.mutate(f.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors p-1">
                  <Trash2 size={15} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
