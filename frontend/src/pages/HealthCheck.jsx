import { useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Upload, Camera, AlertTriangle, CheckCircle, Loader2, FlaskConical } from "lucide-react";
import toast from "react-hot-toast";
import { aiApi } from "../api/ai";
import { fieldsApi } from "../api/fields";
import { plantingsApi } from "../api/plantings";

const SEVERITY_CONFIG = {
  low: { label: "Hafif", color: "bg-yellow-100 text-yellow-700", icon: "⚠️" },
  medium: { label: "Orta", color: "bg-orange-100 text-orange-700", icon: "🔶" },
  high: { label: "Ağır", color: "bg-red-100 text-red-700", icon: "🚨" },
};

function ImageDropzone({ onFile, preview }) {
  const inputRef = useRef();
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file?.type.startsWith("image/")) onFile(file);
  };

  return (
    <div
      className={`border-2 border-dashed rounded-xl transition-colors cursor-pointer
        ${dragging ? "border-primary-400 bg-primary-50" : "border-gray-300 hover:border-primary-400 hover:bg-gray-50"}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current.click()}
    >
      {preview ? (
        <div className="relative">
          <img src={preview} alt="Yüklenen" className="w-full h-56 object-cover rounded-xl" />
          <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-xl opacity-0 hover:opacity-100 transition-opacity">
            <p className="text-white text-sm font-medium">Değiştirmek için tıklayın</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-14 text-gray-400 space-y-2">
          <Camera size={40} />
          <p className="text-sm font-medium">Fotoğraf sürükleyin veya tıklayın</p>
          <p className="text-xs">PNG, JPG, WEBP — max 10MB</p>
        </div>
      )}
      <input ref={inputRef} type="file" accept="image/*" className="hidden"
        onChange={(e) => { if (e.target.files[0]) onFile(e.target.files[0]); }} />
    </div>
  );
}

function ResultCard({ result }) {
  const sev = SEVERITY_CONFIG[result.severity] || SEVERITY_CONFIG.low;
  const isHealthy = result.detected_disease?.toLowerCase().includes("healthy") || result.detected_disease?.includes("Sağlıklı");

  return (
    <div className={`card space-y-4 ${isHealthy ? "border-green-200 bg-green-50" : "border-orange-200 bg-orange-50"}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            {isHealthy
              ? <CheckCircle size={20} className="text-green-600" />
              : <AlertTriangle size={20} className="text-orange-600" />
            }
            <h3 className="font-bold text-gray-900">{result.detected_disease}</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sev.color}`}>
              {sev.icon} {sev.label} şiddet
            </span>
            <span className="text-xs text-gray-500">
              Güven: %{Math.round(result.confidence * 100)}
            </span>
            {result.demo_mode && (
              <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full flex items-center gap-1">
                <FlaskConical size={10} /> Demo
              </span>
            )}
          </div>
        </div>
      </div>

      {!isHealthy && (
        <>
          <div>
            <p className="text-xs font-semibold text-gray-700 mb-1">Tedavi Önerisi</p>
            <p className="text-sm text-gray-600 bg-white rounded-lg p-3 border border-gray-200">
              {result.treatment}
            </p>
          </div>

          {result.similar_diseases?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-1">Benzer Hastalıklar</p>
              <div className="flex flex-wrap gap-1">
                {result.similar_diseases.map((d, i) => (
                  <span key={i} className="text-xs bg-white border border-gray-200 rounded-full px-2 py-0.5 text-gray-600">
                    {d}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function HealthCheck() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [selectedField, setSelectedField] = useState("");
  const [selectedPlanting, setSelectedPlanting] = useState("");
  const [result, setResult] = useState(null);

  const { data: fields = [] } = useQuery({
    queryKey: ["fields"],
    queryFn: () => fieldsApi.list().then(r => r.data.data),
  });

  const { data: plantings = [] } = useQuery({
    queryKey: ["plantings"],
    queryFn: () => plantingsApi.list().then(r => r.data.data),
  });

  const activePlantings = plantings.filter(p =>
    p.status === "active" && (!selectedField || p.field_id === selectedField)
  );

  const detectMutation = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      fd.append("image", file);
      if (selectedField) fd.append("field_id", selectedField);
      if (selectedPlanting) fd.append("planting_id", selectedPlanting);
      return aiApi.detectDisease(fd);
    },
    onSuccess: (res) => {
      setResult(res.data.data);
      toast.success("Analiz tamamlandı");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Analiz başarısız");
    },
  });

  const handleFile = (f) => {
    setFile(f);
    setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(f);
  };

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Bitki Sağlığı</h1>
        <p className="text-gray-500 text-sm mt-1">
          Hasta görünen bitkinin fotoğrafını yükleyin — AI hastalığı tespit eder
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Sol: Yükleme */}
        <div className="space-y-3">
          <ImageDropzone onFile={handleFile} preview={preview} />

          <div className="grid grid-cols-2 gap-2">
            <select className="input-field" value={selectedField}
              onChange={(e) => { setSelectedField(e.target.value); setSelectedPlanting(""); }}>
              <option value="">Tarla (opsiyonel)</option>
              {fields.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
            <select className="input-field" value={selectedPlanting}
              onChange={(e) => setSelectedPlanting(e.target.value)}>
              <option value="">Ekim (opsiyonel)</option>
              {activePlantings.map(p => <option key={p.id} value={p.id}>{p.crop_type}</option>)}
            </select>
          </div>

          <button
            className="btn-primary w-full flex items-center justify-center gap-2"
            disabled={!file || detectMutation.isPending}
            onClick={() => detectMutation.mutate()}
          >
            {detectMutation.isPending
              ? <><Loader2 size={16} className="animate-spin" /> Analiz ediliyor...</>
              : <><Upload size={16} /> Hastalık Tespiti Yap</>
            }
          </button>

          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-xs text-green-700">
            <strong>Model durumu:</strong> EfficientNet-B3 — PlantVillage dataset ile eğitildi (%99.5 doğruluk). 38 hastalık sınıfı destekleniyor.
          </div>
        </div>

        {/* Sağ: Sonuç */}
        <div>
          {detectMutation.isPending && (
            <div className="card flex flex-col items-center justify-center h-64 text-gray-400">
              <Loader2 size={36} className="animate-spin mb-3 text-primary-500" />
              <p className="text-sm">AI modeli analiz ediyor...</p>
              <p className="text-xs mt-1">Bu birkaç saniye sürebilir</p>
            </div>
          )}

          {result && !detectMutation.isPending && <ResultCard result={result} />}

          {!result && !detectMutation.isPending && (
            <div className="card flex flex-col items-center justify-center h-64 text-gray-300">
              <Camera size={48} className="mb-3" />
              <p className="text-sm">Fotoğraf yükleyip analiz başlatın</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
