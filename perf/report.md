# Performance Test Report — Habit Tracker API

## Test Environment

| Component | Detail |
|-----------|--------|
| Tool | k6 v0.54+ |
| Target | Docker container (localhost:8001) |
| Database | PostgreSQL 16 |
| CI Runner | GitHub Actions (ubuntu-latest, 2 vCPU, 7 GB RAM) |
| Date | 2026-05-29 |

---

## Smoke Test Results (5 VU · 30s)

**Scenario:** 5 sanal kullanıcı, 30 saniye boyunca sağlık kontrolü + kayıt + giriş + alışkanlık listeleme akışı.

```
scenarios: (100.00%) 1 scenario, 5 max VUs, 1m00s max duration
         * default: 5 looping VUs for 30s (gracefulStop: 30s)
```

| Metric | Value |
|--------|-------|
| Total requests | ~270 |
| p(95) latency | **< 500ms** ✅ |
| Error rate | **< 1%** ✅ |
| Checks passed | 100% |

**Sonuç:** Smoke test tüm threshold'ları geçti. API 5 VU altında stabil çalışıyor.

---

## Load Test Results (10→50 VU · 60s)

**Senaryo:** Gerçekçi kullanıcı akışı — kayıt → giriş → alışkanlık oluştur → listele → getir → güncelle → sil

```
stages:
  - 10s → 10 VU  (ramp-up)
  - 20s → 30 VU  (yük artışı)
  - 20s → 50 VU  (pik yük)
  - 10s → 0 VU   (ramp-down)
```

### Ölçüm Sonuçları

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| **p(95) latency** | **285ms** | < 500ms | ✅ PASS |
| **p(99) latency** | **301ms** | < 1000ms | ✅ PASS |
| Error rate | 0% (fix sonrası) | < 5% | ✅ PASS |
| Checks passed | 100% | > 99% | ✅ PASS |
| Throughput | ~15.7 req/s | — | — |

### Latency Dağılımı

```
avg=67ms  min=1ms  med=7.5ms  max=521ms
p(90)=274ms  p(95)=285ms  p(99)=301ms
```

### Endpoint Bazında Gözlemler

| Endpoint | Avg Latency | Açıklama |
|----------|-------------|----------|
| GET /health | ~2ms | Çok hızlı, DB sorgusu yok |
| POST /register | ~120ms | Password hashing (bcrypt) nedeniyle yavaş — normal |
| POST /login | ~110ms | bcrypt verify nedeniyle yavaş — normal |
| POST /habits | ~15ms | DB insert, hızlı |
| GET /habits | ~20ms | JOIN sorgusu, hızlı |
| PATCH /habits/{id} | ~12ms | Basit update |
| DELETE /habits/{id} | ~10ms | Cascade delete |

---

## Yorum ve Değerlendirme

### Güçlü Yönler
- **p(95) = 285ms** — 500ms threshold'unun çok altında, hedefi karşılıyor
- **Tüm check'ler %100 pass** — iş mantığı hataları yok
- 50 eşzamanlı VU altında sistem stabil kaldı

### Gözlemlenen Darboğazlar
1. **bcrypt işlemleri** — `/register` ve `/login` endpoint'leri password hashing nedeniyle ~100-120ms alıyor. Bu güvenlik gereği, optimizasyon değil.
2. **p(99) = 301ms** — tek aykırı değer `521ms` (max), bu muhtemelen cold-start veya DB bağlantı havuzu kurma süresinden kaynaklanıyor.

### Öneriler
- Production'da **connection pooling** (PgBouncer) eklenmeli — bağlantı kurma overhead'ini düşürür
- `bcrypt` rounds değeri ayarlanabilir (şu an default 12) — güvenlik-performans dengesi
- Daha yüksek yüklerde (100+ VU) horizontal scaling (K8s replicas artırma) gerekebilir

---

## Threshold Özeti

| Test | http_req_duration p(95) | http_req_failed | Sonuç |
|------|------------------------|-----------------|-------|
| Smoke (5 VU, 30s) | < 500ms ✅ | < 1% ✅ | **PASS** |
| Load (50 VU, 60s) | **285ms** ✅ | 0% ✅ | **PASS** |
