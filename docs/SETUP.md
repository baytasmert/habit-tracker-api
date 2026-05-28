# Setup & Installation Guide

Complete step-by-step instructions for setting up the Habit Tracker API project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development with Docker Compose](#local-development)
3. [Manual Setup (Without Docker)](#manual-setup)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- **Git**: Version control (https://git-scm.com/)
- **Docker & Docker Compose**: Containerization
  - [Install Docker](https://docs.docker.com/get-docker/)
  - Docker Compose comes with Docker Desktop
- **Python 3.11+**: Programming language
  - [Download Python](https://www.python.org/downloads/)

### Optional (for specific tasks)
- **kubectl**: Kubernetes CLI (for K8s deployment)
- **kind**: Kubernetes in Docker (for local K8s testing)
- **k6**: Performance testing (for load tests)
- **Playwright**: Browser automation (for E2E tests)

### System Requirements
- **Disk Space**: 5GB (for Docker images + PostgreSQL data)
- **RAM**: 4GB minimum (Docker + application)
- **CPU**: 2+ cores recommended

---

## Local Development with Docker Compose

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/habit_tracker_api-1.git
cd habit_tracker_api-1
```

### Step 2: Verify Docker Installation

```bash
docker --version
docker-compose --version
```

Expected output:
```
Docker version 24.0.x
Docker Compose version 2.x.x
```

### Step 3: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

Review `.env` for any customization (defaults are fine for local dev):

```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/habits
DB_HOST=db
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=habits

# API
API_PORT=8000
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# S3
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
S3_BUCKET=habits
S3_ENDPOINT_URL=http://localstack:4566

# Monitoring
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
```

### Step 4: Start All Services

```bash
docker-compose up -d
```

This starts:
- **API** on http://localhost:8001
- **PostgreSQL** on localhost:5432
- **LocalStack (S3)** on localhost:4566
- **Prometheus** on http://localhost:9090
- **Grafana** on http://localhost:3000
- **Jaeger** on http://localhost:16686

Verify all services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  STATUS
habit_tracker_api   "uvicorn src.main:..."   Up (healthy)
postgres            "postgres"               Up (healthy)
localstack          "docker-entrypoint..."   Up
prometheus          "/bin/prometheus..."     Up
grafana             "/run.sh"                Up
jaeger              "/go/bin/all-in-on..."   Up
```

### Step 5: Access the Application

Open your browser to:

- **Web UI**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs (Swagger)
- **API ReDoc**: http://localhost:8001/redoc
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

### Step 6: Register & Login

1. Navigate to http://localhost:8001/register
2. Create a user account:
   - Username: `testuser`
   - Password: `testpass123`
3. You're redirected to login
4. Login with the same credentials
5. Access your dashboard with habit management

### Step 7: View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db

# Real-time logs (last 100 lines)
docker-compose logs -f --tail=100
```

### Step 8: Stop Services

```bash
# Stop (keep data)
docker-compose stop

# Stop and remove containers (keep volumes)
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

---

## Manual Setup (Without Docker)

If you prefer to run the application locally without Docker.

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Install & Start PostgreSQL

**macOS (Homebrew)**:
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Windows (Installer)**:
- Download from https://www.postgresql.org/download/windows/
- Run installer, remember password for postgres user

**Linux (apt)**:
```bash
sudo apt-get install postgresql-16
sudo systemctl start postgresql
```

Verify PostgreSQL is running:
```bash
psql --version
psql -U postgres -c "SELECT version();"
```

### Step 3: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE habits;

# Create user
CREATE USER user WITH PASSWORD 'password';

# Grant privileges
ALTER ROLE user SET client_encoding TO 'utf8';
ALTER ROLE user SET default_transaction_isolation TO 'read committed';
ALTER ROLE user SET default_transaction_deferrable TO off;
ALTER ROLE user SET default_transaction_read_only TO off;
ALTER ROLE user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE habits TO user;

# Exit psql
\q
```

### Step 4: Set Environment Variables

Create `.env` file in project root:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/habits
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
API_PORT=8000
```

### Step 5: Initialize Database

```bash
# Database tables are created automatically on startup
# But you can manually initialize with:
python -c "from src.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Step 6: Run the Application

```bash
# Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the FastAPI development server
python -m uvicorn src.main:app --reload
```

Application starts on http://localhost:8000

### Step 7: Install Optional Tools

For development and testing:

```bash
# Playwright (for E2E tests)
pip install playwright
playwright install chromium

# k6 (for performance testing)
# Download from https://k6.io/docs/getting-started/installation/

# Install development dependencies
pip install -r requirements-dev.txt
```

---

## Kubernetes Deployment

### Prerequisites

Install kubectl and kind:

```bash
# macOS
brew install kubectl kind

# Windows (Chocolatey)
choco install kubernetes-cli kind

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
curl -Lo kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x kind
```

### Step 1: Create Kind Cluster

```bash
kind create cluster --name habit-tracker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### Step 2: Build and Load Docker Image

```bash
# Build Docker image
docker build -t habit-tracker-api:latest .

# Load image into Kind cluster
kind load docker-image habit-tracker-api:latest --name habit-tracker

# Verify image is loaded
kind get images --name habit-tracker
```

### Step 3: Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/

# Verify deployments
kubectl get deployments
kubectl get pods
kubectl get services

# Check pod status
kubectl describe pod <pod-name>

# View logs
kubectl logs -f deployment/habit-tracker-api
kubectl logs -f deployment/postgres
```

### Step 4: Access the Application

Option A: Port Forwarding

```bash
# Forward to API
kubectl port-forward svc/habit-tracker-api 8000:8000

# Access on http://localhost:8000
```

Option B: NodePort Service (modify service.yaml)

```yaml
spec:
  type: NodePort
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30000
```

Then access via: `http://<node-ip>:30000`

### Step 5: Monitor Kubernetes Resources

```bash
# Watch pods updating
kubectl get pods --watch

# View resource usage
kubectl top pods
kubectl top nodes

# Get detailed pod information
kubectl describe pod <pod-name>

# View events
kubectl get events
```

### Step 6: Clean Up

```bash
# Delete Kind cluster
kind delete cluster --name habit-tracker

# Or just delete manifests
kubectl delete -f k8s/
```

---

## Configuration

### Environment Variables

Key variables in `.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| DATABASE_URL | postgresql://user:password@db:5432/habits | PostgreSQL connection |
| DEBUG | False | Enable debug mode |
| SECRET_KEY | (must set) | JWT signing key |
| API_PORT | 8000 | FastAPI port |
| OTEL_TRACES_EXPORTER | none | Disable telemetry in tests |
| S3_ENDPOINT_URL | http://localstack:4566 | S3 endpoint (dev) |
| AWS_ACCESS_KEY_ID | test | AWS access key |
| AWS_SECRET_ACCESS_KEY | test | AWS secret key |

### Database Configuration

Connection pooling in `src/database.py`:

```python
# For testing: NullPool (no reuse)
engine = create_engine(database_url, poolclass=NullPool)

# For production: QueuePool (reuse connections)
engine = create_engine(database_url, pool_size=5, max_overflow=10)
```

### Logging Configuration

Logs output to stdout:

```
2026-05-28 10:00:00 | INFO | Uvicorn running on http://0.0.0.0:8000
2026-05-28 10:00:01 | INFO | Database connected
```

Configure in `src/main.py`:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## Testing Setup

### Unit & Integration Tests

```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-cov factory-boy faker testcontainers playwright

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_unit_auth.py::TestPasswordHashing -v
```

### E2E Tests (API Integration)

```bash
# Ensure API is running
docker-compose up -d

# Run API integration tests
pytest tests/e2e/test_e2e.py -v

# Run with API output
pytest tests/e2e/test_e2e.py -v -s
```

### E2E Tests (Browser Automation)

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Ensure API is running
docker-compose up -d

# Run Playwright tests
pytest tests/e2e/test_e2e_playwright.py -v

# Run in headed mode (see browser)
pytest tests/e2e/test_e2e_playwright.py -v --headed

# Run specific test
pytest tests/e2e/test_e2e_playwright.py::TestUserRegistrationE2E::test_register_and_login_through_ui -v --headed
```

### Performance Tests

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/

# Ensure API is running
docker-compose up -d

# Run smoke test
k6 run perf/smoke-test.js

# Run load test
k6 run perf/load-test.js

# Run with custom parameters
k6 run -e API_URL=http://localhost:8001 -e DURATION=2m perf/load-test.js
```

---

## Troubleshooting

### Docker Issues

#### Docker Compose Won't Start

```bash
# Check Docker daemon
docker ps

# Rebuild images (fresh start)
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check service logs
docker-compose logs api
docker-compose logs db
```

#### Port Already in Use

```bash
# Port 8001 is busy
# Option 1: Stop other services using port
lsof -i :8001  # Find what's using it
kill -9 <PID>

# Option 2: Change docker-compose port
# Edit docker-compose.yml:
# ports:
#   - "8002:8000"
```

#### Database Connection Refused

```bash
# Check PostgreSQL is running
docker-compose ps

# PostgreSQL specific checks
docker-compose logs db

# Restart database service
docker-compose restart db

# Force recreate database
docker-compose down -v
docker-compose up -d --build
```

### Application Issues

#### 404 on http://localhost:8001

```bash
# Check if API is serving static files
curl http://localhost:8001/

# Should return HTML content, not 404

# If 404:
# 1. Check docker-compose volume mounts
# 2. Rebuild: docker-compose up -d --build
# 3. Check logs: docker-compose logs api
```

#### Templates Not Found

```bash
# Error: Jinja2 TemplateNotFound
# Cause: templates directory not in Docker image

# Solution 1: Rebuild image
docker-compose build --no-cache

# Solution 2: Check volume mounts in docker-compose.yml
# Should have:
# volumes:
#   - ./templates:/app/templates
#   - ./static:/app/static

# Solution 3: Copy files into container
docker-compose cp templates/. habit_tracker_api:/app/templates
```

#### Registration/Login Not Working

```bash
# Check database connection
docker-compose logs db

# Verify PostgreSQL is healthy
docker-compose exec db pg_isready -U user

# Check API logs
docker-compose logs api

# Test endpoint directly
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"pass"}'
```

### Testing Issues

#### Tests Timeout

```bash
# Increase pytest timeout
pytest tests/e2e/ -v --timeout=30

# Or skip slow tests
pytest tests/ -v -m "not slow"
```

#### Playwright Tests Fail

```bash
# Ensure Playwright is installed
pip install playwright
playwright install chromium

# Run in headed mode to see errors
pytest tests/e2e/test_e2e_playwright.py -v --headed

# Check API is running
curl http://localhost:8001/health

# Run with debug output
pytest tests/e2e/test_e2e_playwright.py -v -s --headed
```

#### k6 Tests Fail

```bash
# Check k6 is installed
k6 version

# Verify API is running
curl http://localhost:8001/health

# Run with verbose output
k6 run -v perf/load-test.js

# Run against different API URL
k6 run -e API_URL=http://localhost:8000 perf/load-test.js
```

### Kubernetes Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>

# Check events
kubectl get events

# Restart pod
kubectl delete pod <pod-name>
```

#### Image Pull Errors

```bash
# For Kind, load image instead of pulling
kind load docker-image habit-tracker-api:latest --name habit-tracker

# Update deployment to use IfNotPresent
kubectl set image deployment/habit-tracker-api \
  api=habit-tracker-api:latest \
  --record

# Check imagePullPolicy in deployment
kubectl get deployment -o yaml | grep imagePullPolicy
```

#### Database Connection Error in K8s

```bash
# Check if postgres pod is running
kubectl get pods -l app=postgres

# Check postgres logs
kubectl logs deployment/postgres

# Verify ConfigMap
kubectl get configmap app-config -o yaml

# Check environment variables in deployment
kubectl exec deployment/habit-tracker-api -- env | grep DATABASE
```

### Performance Issues

#### API Slow Response

```bash
# Check metrics in Prometheus
# Visit http://localhost:9090
# Query: http_request_duration_seconds

# Check database slow queries
docker-compose exec db psql -U user -d habits -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 5;"

# Check resource usage
docker stats
```

#### Load Test Failures

```bash
# Check error rate
k6 run perf/load-test.js

# Look for "http_req_failed" in output

# Common causes:
# 1. Duplicate usernames → Change username generation
# 2. Database connection limit → Increase pool size
# 3. Slow API → Check latency in prometheus

# Run with lower load first
k6 run -e VUS=10 -e DURATION=30s perf/load-test.js
```

### Git Issues

#### Commit Hooks Failing

```bash
# View hook output
git commit -v

# Bypass hooks (not recommended)
git commit --no-verify

# Fix actual issues (recommended)
# Usually flake8 errors
flake8 src/ tests/
autopep8 --in-place --aggressive <file>
```

#### Merge Conflicts

```bash
# View conflicts
git status

# Edit files to resolve conflicts
# Then:
git add .
git commit -m "Resolve merge conflicts"
```

---

## Next Steps

1. **Local Development**: Use `docker-compose up` for development
2. **Testing**: Run `pytest tests/ -v` regularly
3. **Code Quality**: Check with `flake8 src/ tests/`
4. **Git Workflow**: Commit frequently, push to GitHub
5. **CI/CD**: Push to main → GitHub Actions runs automatically

---

## Getting Help

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Docker Docs**: https://docs.docker.com/
- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Playwright Docs**: https://playwright.dev/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**See README.md for quick start, ARCHITECTURE.md for technical details.**
