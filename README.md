# Habit Tracker API

**Marmara Üniversitesi — Bulut Mimarilerinde Test Mühendisliği — Dönem Projesi**

Günlük alışkanlık takibi, streak hesaplama ve kullanıcı istatistikleri sunan bir REST API. Proje amacı "karmaşık uygulama yazmak" değil, "basit uygulama için endüstri standardında test ve dağıtım altyapısı kurmak"tır.

---

## Özellikler

- **REST API**: FastAPI, 12+ endpoint, JWT auth, bcrypt, rate limiting
- **Veritabanı**: PostgreSQL 16, SQLAlchemy ORM, streak hesaplama
- **Web UI**: NGINX + Jinja2 template — Playwright E2E testleri için
- **AWS S3**: LocalStack üzerinden avatar upload/download
- **Testing**: 92 test — unit, integration, Testcontainers, E2E, Postman/Newman
- **CI/CD**: GitHub Actions 6 job — lint → test → build → deploy → smoke → load
- **Kubernetes**: Kind cluster deploy, Deployment + Service + ConfigMap + Ingress
- **Monitoring**: Prometheus metrics, Grafana 4 panel dashboard
- **Tracing**: OpenTelemetry + Jaeger (OTLP gRPC) — **+5 bonus**
- **ArgoCD**: GitOps manifests — **+5 bonus**
- **Performance**: k6 smoke (5VU/30s) + load test (50VU/60s), p95=285ms

---

## Mimari

```
Browser
  │
  ├── :8001 ──→ NGINX (frontend proxy / static files)
  │                  │
  └── :8000 ──→ FastAPI (REST API + Jinja2 templates)
                    │
          ┌─────────┼──────────────────┐
          │         │                  │
    PostgreSQL  LocalStack S3      Jaeger:4317
      :5432     :4566 (avatars)   (OTLP tracing)
          │
    Prometheus:9090 → Grafana:3000
```

Tam diyagram: [docs/architecture.png](docs/architecture.png)

---

## Hızlı Başlangıç

### Gereksinimler
- Docker & Docker Compose
- Python 3.11+

### Docker Compose ile Başlatma

```bash
git clone https://github.com/baytasmert/habit-tracker-api.git
cd habit-tracker-api
cp .env.docker .env
docker-compose up -d
```

| Servis | URL | Açıklama |
|--------|-----|----------|
| **Web UI + API** | http://localhost:8000 | FastAPI — login/register/home sayfaları + REST endpoint'leri |
| API Docs (Swagger) | http://localhost:8000/docs | Interaktif API dokümantasyonu |
| Static Files | http://localhost:8001 | NGINX — sadece CSS/JS static dosyaları |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | Metrikler |
| Jaeger UI | http://localhost:16686 | Distributed tracing |

---

## API Endpoint'leri

| Method | Endpoint | Auth | Açıklama |
|--------|----------|------|----------|
| POST | /register | — | Kullanıcı kaydı |
| POST | /login | — | JWT token al |
| GET | /health | — | Sağlık kontrolü |
| GET | /metrics | — | Prometheus metrikleri |
| GET | /me | ✓ | Mevcut kullanıcı |
| GET | /habits | ✓ | Alışkanlık listesi |
| POST | /habits | ✓ | Alışkanlık oluştur |
| GET | /habits/{id} | ✓ | Detay |
| PATCH | /habits/{id} | ✓ | Güncelle |
| DELETE | /habits/{id} | ✓ | Sil |
| POST | /habits/{id}/track | ✓ | Günlük takip ekle |
| GET | /habits/{id}/streak | ✓ | Seri hesapla |
| POST | /avatars/{id} | ✓ | Avatar yükle (S3) |
| GET | /avatars/{id} | — | Avatar getir (S3) |

---

## Testler

### Unit & Integration (pytest)

```bash
# Lokal PostgreSQL gerektirir (docker-compose up -d db)
pytest tests/ --ignore=tests/e2e --ignore=tests/test_testcontainers.py -v

# Coverage ile
pytest tests/ --ignore=tests/e2e --cov=src --cov-report=html
open htmlcov/index.html
```

### Testcontainers (Gerçek PostgreSQL container)

```bash
# Linux/CI'da çalışır (Docker daemon gerektirir)
pytest tests/test_testcontainers.py -v
# 4 test: schema, register, CRUD, persistence
```

### E2E (Playwright — 6 senaryo)

```bash
# docker-compose up -d ile API çalışıyor olmalı
playwright install chromium
pytest tests/e2e/ -v
```

| # | Senaryo | Durum |
|---|---------|-------|
| 1 | Kullanıcı kaydı ve giriş | ✅ |
| 2 | Alışkanlık oluştur ve listede gör | ✅ |
| 3 | Alışkanlık takip et ve seri gör | ✅ |
| 4 | Alışkanlık düzenle | ✅ |
| 5 | Yetkisiz erişim login'e yönlendirir | ✅ |
| 6 | Geçersiz login hata gösterir | ✅ |

### Postman / Newman

```bash
npm install -g newman
newman run postman/HabitTrackerAPI.postman_collection.json \
  --environment postman/environment.json \
  --env-var base_url=http://localhost:8001
```

### Performans (k6)

```bash
# docker-compose up -d ile API çalışıyor olmalı

# Smoke test (5 VU, 30s)
k6 run -e BASE_URL=http://localhost:8001 perf/smoke-test.js

# Load test (10→50 VU, 60s)
k6 run -e BASE_URL=http://localhost:8001 perf/load-test.js
```

Sonuçlar: [perf/report.md](perf/report.md) — p95=285ms, 0% hata oranı ✅

---

## Kubernetes (Kind)

```bash
# Kind cluster oluştur
kind create cluster --name habit-tracker

# Image yükle
docker build -t habit-tracker-api:latest .
kind load docker-image habit-tracker-api:latest --name habit-tracker

# Deploy et
kubectl apply -f k8s/postgres.yaml
kubectl rollout status deployment/postgres -n default --timeout=2m
kubectl apply -f k8s/jaeger.yaml
kubectl apply -f k8s/localstack.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/habit-tracker-api -n default --timeout=5m

# Erişim
kubectl port-forward svc/habit-tracker-api-service 8001:8001

# Temizlik
kind delete cluster --name habit-tracker
```

---

## CI/CD Pipeline

```
push/PR → main
    │
    ├── lint         flake8 kod kalite (10 dk)
    ├── test         pytest + coverage ≥70% + LocalStack S3 (45 dk)
    ├── build        Docker image → GHCR (:sha + :latest) (20 dk)
    ├── deploy-and-test  Kind K8s deploy + Newman + Playwright E2E (25 dk)
    ├── smoke-test   k6 smoke (5VU/30s) — GHCR imajı (15 dk)
    └── load-test    k6 load (50VU/60s) — GHCR imajı (15 dk)
```

Tüm smoke/load-test job'ları build'deki **aynı GHCR imajını** kullanır (`:sha` tag).

---

## Monitoring

### Prometheus Metrikleri (`/metrics`)

| Metrik | Tip | Açıklama |
|--------|-----|----------|
| `http_requests_total` | Counter | Endpoint/method/status bazlı istek sayısı |
| `http_request_duration_seconds` | Histogram | Latency dağılımı (p50/p95/p99) |
| `http_requests_in_progress` | Gauge | Anlık işlenen istek sayısı |

### Grafana Dashboard (4 Panel)
- Request Rate (5m)
- Total Requests by Endpoint
- Request Latency (p95, p99)
- Business Metrics

### OpenTelemetry Tracing (+5 bonus)
FastAPI + SQLAlchemy otomatik enstrümantatyon. OTLP gRPC → Jaeger:4317.

---

## Proje Yapısı

```
habit-tracker-api/
├── src/                    # FastAPI uygulama
│   ├── main.py             # Endpoint'ler, middleware
│   ├── models.py           # User, Habit, HabitLog
│   ├── schemas.py          # Pydantic DTO'lar
│   ├── auth.py             # JWT + bcrypt
│   ├── database.py         # PostgreSQL bağlantısı
│   ├── metrics.py          # Prometheus counter/histogram
│   └── aws/s3_service.py   # LocalStack S3
├── templates/              # Jinja2 HTML şablonları
├── static/                 # CSS + JS
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── factories.py        # Factory Boy (User/Habit/HabitLog)
│   ├── unit/               # Birim testler
│   ├── integration/        # Entegrasyon testleri (TestClient)
│   ├── test_testcontainers.py  # Gerçek PostgreSQL container testleri
│   └── e2e/                # Playwright E2E testleri
├── postman/                # Postman koleksiyonu + environment
├── k8s/                    # Kubernetes manifestleri
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── postgres.yaml
│   ├── jaeger.yaml
│   ├── localstack.yaml
│   ├── prometheus.yaml
│   ├── grafana.yaml
│   ├── ingress.yaml
│   └── argocd-app.yaml     # GitOps (+5 bonus)
├── perf/
│   ├── smoke-test.js       # k6 smoke (5VU/30s)
│   ├── load-test.js        # k6 load (10→50VU/60s)
│   └── report.md           # p95 sonuçları ve yorum
├── docs/
│   ├── architecture.png    # Sistem mimarisi diyagramı
│   └── final-report.pdf    # 5 sayfalık final rapor
├── grafana/provisioning/   # Grafana dashboard + datasource
├── .github/workflows/      # CI/CD pipeline
│   └── ci-cd.yml
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Lokal geliştirme ortamı
├── requirements.txt
└── LICENSE                 # MIT
```

---

## Teknoloji Stack

| Katman | Teknoloji |
|--------|-----------|
| Backend | FastAPI 0.110, Python 3.11 |
| Veritabanı | PostgreSQL 16, SQLAlchemy 2.0 |
| Auth | JWT (python-jose), bcrypt, passlib |
| Frontend | NGINX, Jinja2, HTML/CSS/JS |
| Testing | pytest, Factory Boy, Faker, Playwright, k6 |
| Containers | Docker multi-stage, Docker Compose |
| Orchestration | Kubernetes, Kind |
| CI/CD | GitHub Actions, GHCR |
| Monitoring | Prometheus, Grafana, OpenTelemetry, Jaeger |
| AWS | LocalStack S3 (boto3) |

---

## Şartname Karşılama Durumu

| Gereksinim | Durum | Detay |
|------------|-------|-------|
| Mini Servis (4-6 endpoint) | ✅ | 14 endpoint, 3 entity |
| Pytest ≥%70 coverage | ✅ | 92 test, hedef karşılandı |
| Postman/Newman CI | ✅ | 5+ istek, CI'da çalışıyor |
| Docker multi-stage | ✅ | builder + runtime |
| LocalStack S3 | ✅ | Avatar upload/download |
| Testcontainers (≥2 test) | ✅ | 4 test, gerçek PostgreSQL |
| Factory Boy + Faker | ✅ | UserFactory/HabitFactory/LogFactory |
| Kubernetes | ✅ | Kind cluster, tüm manifestler |
| GitHub Actions | ✅ | 6 job pipeline |
| Prometheus + Grafana ≥3 panel | ✅ | 4 panel dashboard |
| k6 + p95 ölçümü | ✅ | p95=285ms (bkz. perf/report.md) |
| E2E 3-5 senaryo | ✅ | 6/6 Playwright testi PASS |
| docs/architecture.png | ✅ | Tam sistem diyagramı |
| docs/final-report.pdf | ✅ | 5 sayfa, IEEE formatı |
| **Bonus: OpenTelemetry** | ✅ | +5 — OTLP → Jaeger |
| **Bonus: ArgoCD GitOps** | ✅ | +5 — k8s/argocd-app.yaml |

---

## Ortam Değişkenleri

Örnek: `.env.docker` (docker-compose için), `.env.local` (lokal için)

```bash
DATABASE_URL=postgresql://user:password@db:5432/habits
SECRET_KEY=change-in-production
AWS_ENDPOINT_URL=http://localstack:4566
JAEGER_HOST=jaeger
ENABLE_TRACING=true
```

---

## Lisans

MIT License — bkz. [LICENSE](LICENSE)

## Yazar

**Mert Baytaş** — Marmara Üniversitesi, Bilgisayar Mühendisliği  
MTH2526-B25 — Bulut Mimarilerinde Test Mühendisliği, 2025-2026 Bahar
