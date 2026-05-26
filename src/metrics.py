"""
Prometheus Metrics Definitions
Habit Tracker API metrics for monitoring
"""
from prometheus_client import Counter, Histogram, Gauge

# ===== COUNTERS (Sadece Artar) =====

# Tüm HTTP request'leri say
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests received',
    ['method', 'endpoint', 'status']
)

# HTTP hatalarını say
http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status']
)

# Oluşturulan habit'leri say
habits_created_total = Counter(
    'habits_created_total',
    'Total habits created'
)

# Tracking entry'lerini say
habit_logs_created_total = Counter(
    'habit_logs_created_total',
    'Total habit logs created (tracking entries)'
)

# ===== HISTOGRAMS (Dağılım/Percentile) =====

# HTTP request süresi
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

# Streak hesaplama süresi
streak_computation_duration_seconds = Histogram(
    'streak_computation_duration_seconds',
    'Time to compute streak for a habit',
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1)
)

# ===== GAUGES (Anlık Değer) =====

# Aktif DB bağlantıları
database_connections = Gauge(
    'database_connections',
    'Number of active database connections'
)

# Toplam habit sayısı
habits_total = Gauge(
    'habits_total',
    'Total number of habits in the database'
)
