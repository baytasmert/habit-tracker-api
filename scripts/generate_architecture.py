"""Generate docs/architecture.png — Habit Tracker Architecture Diagram"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(18, 12))
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

# Color palette
C = {
    'user':   '#4A90D9',
    'nginx':  '#E67E22',
    'api':    '#27AE60',
    'db':     '#8E44AD',
    's3':     '#E74C3C',
    'jaeger': '#16A085',
    'prom':   '#D35400',
    'grafana':'#2980B9',
    'k8s':    '#2C3E50',
    'ci':     '#7F8C8D',
    'border': '#BDC3C7',
    'text':   '#2C3E50',
    'arrow':  '#95A5A6',
    'bg':     '#ECF0F1',
}

def box(ax, x, y, w, h, label, sublabel='', color='#3498DB', fontsize=9):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor='white',
                          linewidth=1.5, alpha=0.92, zorder=3)
    ax.add_patch(rect)
    cy = y + h / 2
    if sublabel:
        ax.text(x + w/2, cy + 0.12, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color='white', zorder=4)
        ax.text(x + w/2, cy - 0.22, sublabel, ha='center', va='center',
                fontsize=7, color='white', alpha=0.85, zorder=4)
    else:
        ax.text(x + w/2, cy, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color='white', zorder=4)

def section(ax, x, y, w, h, title, color='#ECF0F1'):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.15",
                          facecolor=color, edgecolor=C['border'],
                          linewidth=1.5, alpha=0.5, zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.2, y + h - 0.3, title, ha='left', va='top',
            fontsize=8, color='#555', style='italic', zorder=2)

def arrow(ax, x1, y1, x2, y2, label='', color='#7F8C8D'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color,
                                lw=1.4, connectionstyle='arc3,rad=0.0'),
                zorder=5)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.12, label, ha='center', va='bottom',
                fontsize=6.5, color='#555', zorder=6)

# ── Title ──────────────────────────────────────────────────────────────────
ax.text(9, 11.6, 'Habit Tracker API — Mimari Diyagram',
        ha='center', va='center', fontsize=14, fontweight='bold', color=C['text'])
ax.text(9, 11.2, 'FastAPI · PostgreSQL · LocalStack S3 · Prometheus · Grafana · Jaeger · Kubernetes · CI/CD',
        ha='center', va='center', fontsize=8, color='#7F8C8D')

# ── Section: Client ──────────────────────────────────────────────────────
section(ax, 0.3, 8.8, 2.5, 1.8, 'Client', '#EBF5FB')
box(ax, 0.6, 9.2, 1.8, 1.1, '🌐 Browser', 'User / Playwright E2E', C['user'])

# ── Section: Docker Compose / Runtime ───────────────────────────────────
section(ax, 3.2, 5.0, 11.2, 5.5, 'Docker Compose / Kubernetes (Kind)', '#EAF7F0')

# NGINX
box(ax, 3.5, 8.8, 2.2, 1.1, '🔀 NGINX', ':8001 Frontend', C['nginx'])
# API
box(ax, 6.5, 8.8, 2.5, 1.1, '⚡ FastAPI', ':8000 API', C['api'])
# Postgres
box(ax, 3.5, 6.8, 2.2, 1.4, '🐘 PostgreSQL', ':5432\nHabits DB', C['db'])
# LocalStack
box(ax, 6.5, 6.8, 2.5, 1.4, '📦 LocalStack', ':4566\nS3 Avatars', C['s3'])
# Jaeger
box(ax, 9.8, 8.8, 2.2, 1.1, '🔍 Jaeger', ':16686 Tracing', C['jaeger'])
# Prometheus
box(ax, 3.5, 5.2, 2.2, 1.1, '📊 Prometheus', ':9090 Metrics', C['prom'])
# Grafana
box(ax, 6.5, 5.2, 2.5, 1.1, '📈 Grafana', ':3000 Dashboard', C['grafana'])

# ── Section: CI/CD ────────────────────────────────────────────────────────
section(ax, 14.8, 5.0, 2.8, 5.5, 'CI/CD', '#FEF9E7')
box(ax, 15.0, 9.0, 2.4, 0.9, '🐙 GitHub\nActions', '', C['ci'], fontsize=8)
box(ax, 15.0, 7.8, 2.4, 0.9, '🐳 GHCR\nRegistry', '', '#2C3E50', fontsize=8)
box(ax, 15.0, 6.6, 2.4, 0.9, '☸ Kind\nCluster', '', C['k8s'], fontsize=8)
box(ax, 15.0, 5.4, 2.4, 0.9, '📬 Newman\n+ Playwright', '', C['user'], fontsize=8)

# ── Section: Tests ────────────────────────────────────────────────────────
section(ax, 0.3, 0.5, 14.2, 4.0, 'Test Katmanları', '#FDF2F8')
box(ax, 0.6, 2.8, 2.8, 1.3, '🔬 Unit Tests', 'pytest · 70%+ cov', '#8E44AD')
box(ax, 3.8, 2.8, 2.8, 1.3, '🔗 Integration', 'TestContainers\nFactory Boy · Faker', '#27AE60')
box(ax, 6.9, 2.8, 2.8, 1.3, '🌐 E2E Tests', 'Playwright\n6 Senaryo', '#E67E22')
box(ax, 10.0, 2.8, 2.8, 1.3, '⚡ Perf Tests', 'k6 · p95=285ms\nSmoke + Load', '#E74C3C')
box(ax, 0.6, 1.0, 3.0, 1.3, '📫 Postman/Newman', '5+ endpoint\nCI\'da koşar', '#16A085')
box(ax, 4.0, 1.0, 3.0, 1.3, '☁️ LocalStack S3', 'S3 upload/download\ntest edildi', '#D35400')
box(ax, 7.3, 1.0, 3.0, 1.3, '🔍 OpenTelemetry', 'OTLP gRPC\nJaeger tracing +5', '#2C3E50')
box(ax, 10.6, 1.0, 3.0, 1.3, '🎯 ArgoCD', 'GitOps\nk8s/argocd-app.yaml', '#8E44AD')

# ── Arrows ────────────────────────────────────────────────────────────────
# Browser → NGINX
arrow(ax, 2.4, 9.75, 3.5, 9.75, 'HTTP :8001')
# Browser → API (direct for REST)
arrow(ax, 2.4, 9.4, 6.5, 9.4, 'API :8000')
# NGINX → API
arrow(ax, 5.7, 9.75, 6.5, 9.75, 'proxy')
# API → Postgres
arrow(ax, 7.5, 8.8, 4.6, 8.2, 'SQLAlchemy')
# API → LocalStack
arrow(ax, 7.5, 8.8, 7.75, 8.2, 'boto3/S3')
# API → Jaeger
arrow(ax, 9.0, 9.35, 9.8, 9.35, 'OTLP:4317')
# API → Prometheus (scrape)
arrow(ax, 5.5, 8.8, 4.6, 6.3, '/metrics')
# Prometheus → Grafana
arrow(ax, 5.7, 5.75, 6.5, 5.75, 'scrape')
# CI → GHCR
arrow(ax, 16.2, 9.0, 16.2, 8.7, 'push :sha')
# GHCR → Kind
arrow(ax, 16.2, 7.8, 16.2, 7.5, 'pull & deploy')

# ── Legend ────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(color=C['user'],   label='Client / Auth'),
    mpatches.Patch(color=C['nginx'],  label='NGINX Proxy'),
    mpatches.Patch(color=C['api'],    label='FastAPI'),
    mpatches.Patch(color=C['db'],     label='PostgreSQL'),
    mpatches.Patch(color=C['s3'],     label='LocalStack S3'),
    mpatches.Patch(color=C['jaeger'], label='Jaeger Tracing'),
    mpatches.Patch(color=C['prom'],   label='Prometheus'),
    mpatches.Patch(color=C['grafana'],label='Grafana'),
    mpatches.Patch(color=C['ci'],     label='GitHub Actions CI/CD'),
]
ax.legend(handles=legend_items, loc='lower right',
          fontsize=7.5, ncol=3, framealpha=0.9,
          bbox_to_anchor=(1.0, 0.0))

os.makedirs('docs', exist_ok=True)
plt.tight_layout()
plt.savefig('docs/architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#f8f9fa')
print("docs/architecture.png saved!")
