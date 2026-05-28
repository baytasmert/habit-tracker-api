# Stage 1: Builder (gerekli paketleri hazırla)
FROM python:3.11-slim AS builder

WORKDIR /app

# requirements.txt'i kopyala ve paketleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime (İnce image - sadece gerekli şeyler)
FROM python:3.11-slim

WORKDIR /app

# Install Playwright browser dependencies and browsers
RUN apt-get update && apt-get install -y \
    libgtk-3-0 libgbm1 libxss1 libnss3 libnspr4 libxshmfence1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Builder'dan yüklenen paketleri kopyala
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Kodunu kopyala
COPY src ./src
COPY tests ./tests
COPY templates ./templates
COPY static ./static
COPY pytest.ini .

# Port expose et
EXPOSE 8000 8001

# Install Playwright browsers
RUN python -m playwright install chromium

# Sunucuyu başlat
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"
