"""Generate docs/final-report.pdf — 5 page final report"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak, Image)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

os.makedirs('docs', exist_ok=True)
doc = SimpleDocTemplate(
    'docs/final-report.pdf',
    pagesize=A4,
    rightMargin=2.5*cm, leftMargin=2.5*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle('Title', parent=styles['Title'],
    fontSize=18, spaceAfter=6, textColor=colors.HexColor('#2C3E50'),
    alignment=TA_CENTER)
subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
    fontSize=11, spaceAfter=4, textColor=colors.HexColor('#7F8C8D'),
    alignment=TA_CENTER)
h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=13, spaceBefore=14, spaceAfter=6,
    textColor=colors.HexColor('#27AE60'),
    borderPad=2)
h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=11, spaceBefore=10, spaceAfter=4,
    textColor=colors.HexColor('#2980B9'))
body_style = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, spaceAfter=6, leading=14, alignment=TA_JUSTIFY)
bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
    fontSize=10, spaceAfter=3, leading=13, leftIndent=15)
code_style = ParagraphStyle('Code', parent=styles['Code'],
    fontSize=8.5, spaceAfter=4, backColor=colors.HexColor('#F4F6F7'),
    borderColor=colors.HexColor('#BDC3C7'), borderWidth=0.5,
    borderPad=4, leftIndent=10)

def hr():
    return HRFlowable(width='100%', thickness=0.5,
                      color=colors.HexColor('#BDC3C7'), spaceAfter=8)

def h1(t): return Paragraph(t, h1_style)
def h2(t): return Paragraph(t, h2_style)
def p(t):  return Paragraph(t, body_style)
def b(t):  return Paragraph(f'• {t}', bullet_style)
def sp(n=6): return Spacer(1, n)

# Table helper
def tbl(data, col_widths, header_color='#27AE60'):
    t = Table(data, colWidths=[w*cm for w in col_widths])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(header_color)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F4F6F7')]),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#BDC3C7')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ])
    t.setStyle(style)
    return t

# ─── CONTENT ─────────────────────────────────────────────────────────────────
story = []

# ── COVER / PAGE 1 ─────────────────────────────────────────────────────────
story += [
    sp(40),
    Paragraph('Habit Tracker API', title_style),
    Paragraph('Bulut Mimarilerinde Test Muhendisligi — Final Rapor', subtitle_style),
    sp(8),
    hr(),
    sp(8),
]

meta = [
    ['Ogrenci', 'Mert Baytas'],
    ['Ders', 'MTH2526-B25 — Bulut Mimarilerinde Test Muhendisligi'],
    ['Egitmen', 'Busra Ayaksiz'],
    ['Universite', 'Marmara Universitesi — Bilgisayar Muhendisligi'],
    ['Konu', 'Habit Tracker API (Gunluk aliskanlik tracking, streak hesapla)'],
    ['Teslim', '4 Haziran 2026'],
    ['Repo', 'github.com/baytasmert/habit-tracker-api'],
]
story.append(tbl(meta, [4, 12], '#2C3E50'))
story += [sp(20), hr(), PageBreak()]

# ── PAGE 2: Giris + Mimari ──────────────────────────────────────────────────
story.append(h1('1. Giris'))
story.append(p(
    'Bu proje, Marmara Universitesi Bilgisayar Muhendisligi bolumunun "Bulut Mimarilerinde '
    'Test Muhendisligi" dersi kapsaminda gelistirilmis bireysel bir donem projesidir. '
    'Proje konusu olarak <b>Habit Tracker API</b> (konu #3) secilmistir: gunluk aliskanlik '
    'takibi, streak hesaplama ve kullanici istatistikleri sunan bir REST API.'
))
story.append(p(
    'Projenin amaci, "karmasik bir uygulama yazmak" degil, "basit bir uygulama icin endustri '
    'standardinda test ve dagitiim altyapisi kurmaktir." Bu dogrultuda FastAPI, PostgreSQL, '
    'LocalStack S3, Docker, Kubernetes, GitHub Actions, Prometheus/Grafana ve k6 gibi araclar '
    'bir arada kullanilmistir.'
))

story.append(h1('2. Mimari'))
story.append(p(
    'Asagidaki diyagram, sistemin tum bilesenlerini gostermektedir. '
    '(docs/architecture.png dosyasinda tam cozunurluklu versiyon mevcuttur.)'
))

# Try to include architecture image
if os.path.exists('docs/architecture.png'):
    try:
        img = Image('docs/architecture.png', width=15*cm, height=9*cm)
        story.append(img)
    except:
        story.append(p('[Mimari diyagram: docs/architecture.png]'))

story.append(sp(6))
story.append(tbl([
    ['Bilesen', 'Teknoloji', 'Port', 'Aciklama'],
    ['REST API', 'FastAPI 0.110', ':8000', 'Habit CRUD, Auth, S3, OTEL'],
    ['Frontend Proxy', 'NGINX', ':8001', 'Static dosyalar, template proxy'],
    ['Veritabani', 'PostgreSQL 16', ':5432', 'Kalici veri, SQLAlchemy ORM'],
    ['Object Storage', 'LocalStack S3', ':4566', 'Avatar/foto yukleme'],
    ['Tracing', 'Jaeger all-in-one', ':16686', 'OpenTelemetry OTLP gRPC'],
    ['Metrics', 'Prometheus', ':9090', 'API metrikleri toplama'],
    ['Dashboard', 'Grafana', ':3000', '4 panel: latency, errors, RPS'],
    ['CI/CD', 'GitHub Actions', '-', 'lint->test->build->deploy->smoke'],
    ['Container Orch.', 'Kubernetes/Kind', '-', 'Deployment+Service+ConfigMap'],
], [4.5, 3.5, 1.8, 6.2], '#27AE60'))
story.append(PageBreak())

# ── PAGE 3: Test Stratejisi ─────────────────────────────────────────────────
story.append(h1('3. Test Stratejisi'))
story.append(p(
    'Test piramidi yaklasimi benimsenmistir: tabanda cok sayida birim test, ortada '
    'entegrasyon testleri ve tepede az sayida E2E test bulunmaktadir. '
    'Toplam 92 test calismakta olup hedef coverage degeri olan %70in ustundedir.'
))
story.append(tbl([
    ['Katman', 'Arac', 'Adet', 'Kapsam'],
    ['Unit Tests', 'pytest', '~40', 'Model validasyon, auth, streak logic'],
    ['Integration Tests', 'pytest + TestClient', '~46', 'API endpoint CRUD, S3, Factory Boy'],
    ['Testcontainers', 'testcontainers-python', '4', 'Gercek PostgreSQL container ile DB akis'],
    ['E2E Tests', 'Playwright', '6', 'Kayit, giris, habit olustur/track/edit/hata'],
    ['API Tests', 'Postman/Newman', '5+', 'Health, register, login, habits, track'],
    ['Perf Tests', 'k6', '2', 'Smoke (5VU/30s) + Load (50VU/60s)'],
], [3.5, 3.5, 1.5, 7.5], '#2980B9'))

story.append(h2('3.1 Test Verisi Uretimi'))
story.append(p(
    'Factory Boy ve Faker kutuphaneleri kullanilarak gercekci test verisi uretilmistir. '
    'UserFactory, HabitFactory ve HabitLogFactory siniflari ile her test izole veri '
    'kullanmakta ve testler arasi bagimlilik ortadan kaldirilmistir.'
))
story.append(Paragraph('<font face="Courier" size="8">tests/factories.py: UserFactory, HabitFactory, HabitLogFactory</font>', code_style))

story.append(h2('3.2 Testcontainers'))
story.append(p(
    'Gercek bir PostgreSQL 16 container ayaga kaldirarak 4 entegrasyon testi calistirilmistir. '
    'Bu testler, sema olusturma, kullanici kaydi, habit CRUD ve veri kaliciligi senaryolarini '
    'kapsamaktadir. Linux/CI ortaminda otomatik olarak calisir.'
))

story.append(h1('4. CI/CD Pipeline'))
story.append(tbl([
    ['Job', 'Amac', 'Suregec', 'Timeout'],
    ['lint', 'flake8 kod kalitesi kontrolu', '-', '10 dk'],
    ['test', 'pytest + coverage >= 70%', 'lint', '45 dk'],
    ['build', 'Docker image insa ve GHCR push', 'lint + test', '20 dk'],
    ['deploy-and-test', 'Kind K8s deploy + Newman + Playwright E2E', 'build', '25 dk'],
    ['smoke-test', 'k6 smoke (5VU/30s) - GHCR imajini kullanir', 'deploy-and-test', '15 dk'],
    ['load-test', 'k6 load (50VU/60s) - GHCR imajini kullanir', 'smoke-test', '15 dk'],
], [2.5, 5.5, 3.0, 1.8], '#16A085'))

story.append(p(
    'Onemli tasarim kararlari: (1) smoke-test ve load-test artik docker build yapmayip '
    'build job\'undan gelen ayni GHCR imajini kullanmaktadir — tutarlilik saglanmistir. '
    '(2) deploy-and-test job\'u Kind cluster uzerinde gercek K8s deployment testi yapar. '
    '(3) Tum job\'lar fail-fast prensibine gore zincirle bagli olup onceki job basarisiz '
    'olursa sonraki calismaz.'
))
story.append(PageBreak())

# ── PAGE 4: Monitoring + Perf ─────────────────────────────────────────────
story.append(h1('5. Monitoring ve Gozlemlenebilirlik'))
story.append(h2('5.1 Prometheus Metrikleri'))
story.append(tbl([
    ['Metrik', 'Tur', 'Aciklama'],
    ['http_requests_total', 'Counter', 'Toplam HTTP istegi sayisi (endpoint, method, status bazinda)'],
    ['http_request_duration_seconds', 'Histogram', 'Istek sure dagilimi (p50, p95, p99)'],
    ['http_requests_in_progress', 'Gauge', 'Su an islenen istek sayisi'],
], [5, 2.5, 8.5], '#D35400'))

story.append(h2('5.2 Grafana Dashboard (4 Panel)'))
story.append(tbl([
    ['Panel', 'Gorsellik', 'Metrik'],
    ['Request Rate (5m)', 'Time series', 'rate(http_requests_total[5m])'],
    ['Total Requests by Endpoint', 'Bar chart', 'sum by(endpoint) http_requests_total'],
    ['Request Latency (p95, p99)', 'Time series', 'histogram_quantile(0.95/0.99, ...)'],
    ['Business Metrics', 'Stat panel', 'Habit/kullanici olusturma oranlari'],
], [4, 3, 9], '#2980B9'))

story.append(h2('5.3 OpenTelemetry Distributed Tracing (+5 Bonus)'))
story.append(p(
    'FastAPI ve SQLAlchemy otomatik olarak enstrumante edilmistir. Spanlar OTLP gRPC '
    'protokolu ile Jaeger\'a iletilmektedir (grpc://jaeger:4317). Her HTTP istek, '
    'DB sorgulari dahil tam trace zincirleriyle goruntulenmektedir.'
))

story.append(h1('6. Performans Raporu'))
story.append(p('k6 ile iki senaryo calistirilmistir. Sonuclar asagidaki gibidir:'))
story.append(tbl([
    ['Test', 'VU', 'Sure', 'p(95)', 'p(99)', 'Hata Orani', 'Sonuc'],
    ['Smoke Test', '5', '30s', '< 500ms', '< 1000ms', '< 1%', 'PASS'],
    ['Load Test', '10->50', '60s', '285ms', '301ms', '0%', 'PASS'],
], [3, 2, 1.5, 2, 2, 2.5, 2], '#E74C3C'))
story.append(sp(6))
story.append(p(
    '<b>Yorum:</b> p(95)=285ms degeri 500ms threshold\'unun cok altindadir. '
    'Yuksek latency gozlemlenen tek islem bcrypt password hashing olup bu bir '
    'guvenlik gereksinimidir, optimize edilmesi onerilmez. 50 esit VU altinda '
    'sistem stabil kalmis, hic check hatasi olusmasmistir.'
))
story.append(PageBreak())

# ── PAGE 5: Sonuc + Ek ──────────────────────────────────────────────────────
story.append(h1('7. Sonuc ve Ogrendiklerim'))
story.append(h2('7.1 Projenin Sayisal Ozeti'))
story.append(tbl([
    ['Olcut', 'Deger'],
    ['Toplam Test Sayisi', '92 test'],
    ['Test Coverage', '>= 70% (hedef karsilandi)'],
    ['E2E Senaryolar', '6/6 PASS (Playwright)'],
    ['API Test', '5+ endpoint (Postman/Newman)'],
    ['k6 p(95) Latency', '285ms (threshold: < 500ms)'],
    ['Docker Image Katmanlari', 'Multi-stage (builder + runtime)'],
    ['K8s Manifest', 'Deployment + Service + ConfigMap'],
    ['Grafana Panel', '4 panel (latency, errors, RPS, business)'],
    ['Bonus', 'OpenTelemetry Tracing (+5) + ArgoCD GitOps (+5)'],
], [6, 10], '#2C3E50'))

story.append(h2('7.2 Karsilasilan Zorluklar'))
story += [
    b('<b>JavaScript SyntaxError:</b> base.html ve habit_detail.html\'de const token '
      'iki kez tanimlanmis, butun script blogu cokuyordu. Playwright pageerror event\'i '
      'ile tespit edildi.'),
    b('<b>CI Pipeline Tutarsizligi:</b> smoke/load-test job\'lari docker build yaparken '
      'build job\'undan farkli imaj olusuyordu. GHCR imajini yeniden kullanan akis '
      'tasarlanarak cozuldu.'),
    b('<b>K8s DNS Sorunu:</b> configmap.yaml\'da AWS_ENDPOINT_URL olarak '
      '"host.docker.internal" kullanilmisti; K8s pod\'larindan bu adrese ulasilamiyor. '
      '"localstack" servis DNS adi ile duzeltildi.'),
    b('<b>Testcontainers Windows Encoding:</b> psycopg2, Windows Turkce locale nedeniyle '
      'hostname\'i UTF-8 olarak ceviremiyordu. Linux/CI ortaminda calisacak sekilde '
      'platformdan bagimsiz yapi kuruldu.'),
]

story.append(h2('7.3 Ileride Yapilabilecekler'))
story += [
    b('PgBouncer connection pooling eklenebilir — yuksek yuk altinda DB baglanti overhead azalir'),
    b('Helm chart ile K8s deploy paketi olusturulabilir (+5 bonus)'),
    b('KEDA ile queue uzunluguna gore otomatik scaling eklenebilir (+5 bonus)'),
    b('Coverage %70 kalitatif olarak yeterli ancak S3 ve OTEL kod yollari icin mock '
      'testler eklenebilir'),
]

story.append(h1('8. Kaynaklar'))
sources = [
    ('FastAPI Docs', 'https://fastapi.tiangolo.com'),
    ('Testcontainers Python', 'https://testcontainers-python.readthedocs.io'),
    ('k6 Documentation', 'https://k6.io/docs'),
    ('OpenTelemetry Python', 'https://opentelemetry-python.readthedocs.io'),
    ('Playwright Python', 'https://playwright.dev/python'),
    ('GitHub Actions Docs', 'https://docs.github.com/actions'),
    ('Kubernetes Docs', 'https://kubernetes.io/docs'),
    ('Prometheus Client Python', 'https://github.com/prometheus/client_python'),
]
story.append(tbl([['Kaynak', 'URL']] + [[s[0], s[1]] for s in sources], [5, 11], '#16A085'))

story += [sp(10), hr(),
          Paragraph('Mert Baytas — Marmara Universitesi, Bilgisayar Muhendisligi, 2026',
                    ParagraphStyle('footer', parent=styles['Normal'],
                                   fontSize=8, textColor=colors.gray, alignment=TA_CENTER))]

doc.build(story)
print("docs/final-report.pdf saved!")
