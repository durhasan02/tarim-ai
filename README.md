# Tarım AI — Akıllı Çiftlik Yönetim Sistemi

Türkiye'deki küçük-orta ölçekli çiftçiler için AI destekli web tabanlı tarım yönetim sistemi.

## Özellikler

| Modül | Açıklama |
|---|---|
| Tarla & Parsel | Leaflet harita üzerinde alan çizimi, PostGIS polygon depolama |
| Ekim Planlama | Ürün kataloğu, ekim-hasat takvimi |
| Sulama & Stok | AI destekli sulama önerisi, gübre/ilaç stok uyarıları |
| Hastalık Tespiti | Fotoğraftan bitki hastalığı tespiti (EfficientNet-B3, 38 sınıf) |
| Hasat & Satış | Verim hesabı, gelir takibi, sezon karşılaştırma |
| Dashboard | Hava durumu uyarıları, özet kartlar, yaklaşan görevler |

## Tech Stack

**Backend** · FastAPI · PostgreSQL + PostGIS · SQLAlchemy · Alembic · Redis · Celery

**Frontend** · React 18 · Tailwind CSS · React Query · Leaflet.js · Recharts · Vite

**AI** · PyTorch (EfficientNet-B3) · scikit-learn · ONNX Runtime

**DevOps** · Docker Compose · GitHub Actions

## Kurulum

```bash
# Repoyu klonla
git clone https://github.com/durhasan02/tarim-ai.git
cd tarim-ai

# Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle (DB şifresi, SECRET_KEY, OpenWeatherMap API key)

# Servisleri başlat
docker compose up -d

# Veritabanı migration
docker compose exec backend alembic upgrade head
```

Uygulama açılışları:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/docs
- AI Servisi: http://localhost:8001/docs

## Proje Yapısı

```
tarim-ai/
├── backend/        # FastAPI uygulaması
│   ├── app/
│   │   ├── api/    # Endpoint'ler
│   │   ├── models/ # SQLAlchemy modelleri
│   │   └── services/
│   └── alembic/    # DB migration'ları
├── frontend/       # React uygulaması
├── ai-service/     # AI modeli servisi (ONNX)
├── ai-models/      # Model eğitim scriptleri
└── docker-compose.yml
```

## Geliştirme Yol Haritası

- [x] Faz 1 — Altyapı (Docker, DB şeması, JWT auth, React iskeleti, CI/CD)
- [ ] Faz 2 — Çekirdek modüller (tarla, ekim, sulama, stok, hasat, dashboard)
- [ ] Faz 3 — AI entegrasyonu (hastalık tespiti, sulama optimizasyonu)
- [ ] Faz 4 — Mobil PWA, testler, deployment

## Lisans

MIT
