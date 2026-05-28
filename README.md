# Habit Tracker API

Bulut Mimarilerinde Test Mühendisliği - University Project

A full-stack habit tracking application with comprehensive testing (unit, integration, E2E), CI/CD automation, containerization, and Kubernetes deployment.

## Features

- **User Management**: Registration, authentication (JWT), password hashing (bcrypt)
- **Habit Management**: CRUD operations, habit tracking, streak calculation
- **Web UI**: Responsive HTML/CSS/JavaScript frontend (no external frameworks)
- **Testing**: 55+ tests (unit, integration, E2E with Playwright)
- **CI/CD**: GitHub Actions pipeline with automated testing and deployment
- **Containerization**: Docker Compose for local development, Docker for production
- **Kubernetes**: Deployment manifests with readiness/liveness probes
- **Monitoring**: Prometheus metrics, Grafana dashboards
- **Distributed Tracing**: OpenTelemetry + Jaeger
- **Performance Testing**: k6 load testing with real user simulations

## Architecture

```
Frontend (HTML/CSS/JS)
    ↓
FastAPI Application (Python)
    ↓ (SQLAlchemy ORM)
PostgreSQL Database
    ↓
External: S3 (LocalStack in dev), Prometheus, Jaeger
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Local Development with Docker Compose

1. **Clone and setup**:
```bash
git clone <repo>
cd habit_tracker_api-1
```

2. **Start all services** (API, PostgreSQL, Grafana, Prometheus, Jaeger):
```bash
docker-compose up -d
```

3. **Access the application**:
- **Web UI**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs (Swagger)
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

4. **View logs**:
```bash
docker-compose logs -f api
```

5. **Stop services**:
```bash
docker-compose down
```

## Testing

### Unit & Integration Tests (56 tests, ~78% coverage)

```bash
# Run all tests
pytest tests/ -v

# Run specific test types
pytest tests/test_unit_auth.py -v              # Unit tests
pytest tests/integration/ -v                    # Integration tests
pytest tests/testcontainers/ -v                # Testcontainers

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

### E2E Tests with Playwright (6 scenarios)

```bash
# Requires docker-compose running
docker-compose up -d

# Run E2E tests
pytest tests/e2e/ -v

# Run in headed mode (see browser)
pytest tests/e2e/ -v --headed

# Run specific scenario
pytest tests/e2e/test_e2e_playwright.py::TestUserRegistrationE2E -v
```

**E2E Test Scenarios**:
1. User registration and login via UI
2. Create habit and view in list
3. Track habit and view streak
4. Edit habit details
5. Delete habit and verify 404
6. Error handling (unauthorized access, invalid login)

### Performance Testing with k6

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/docs/getting-started/installation/

# Requires API running (docker-compose up -d)

# Smoke test (1 VU, 30s)
k6 run perf/smoke-test.js

# Load test (50 VUs, 5min)
k6 run perf/load-test.js

# Custom parameters
k6 run -e API_URL=http://localhost:8001 -e DURATION=2m perf/load-test.js
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /register | No | Register new user |
| POST | /login | No | Login & get JWT token |
| GET | /health | No | Health check |
| GET | /metrics | No | Prometheus metrics |
| GET | /habits | Yes | List user's habits |
| POST | /habits | Yes | Create habit |
| GET | /habits/{id} | Yes | Get habit details |
| PATCH | /habits/{id} | Yes | Update habit |
| DELETE | /habits/{id} | Yes | Delete habit |
| POST | /habits/{id}/track | Yes | Track habit completion |
| GET | /habits/{id}/streak | Yes | Get habit streak |
| POST | /users/{id}/avatar | Yes | Upload avatar to S3 |
| GET | /users/{id}/avatar | Yes | Download avatar from S3 |

## Kubernetes Deployment

### Local Testing with Kind

```bash
# Create Kind cluster
kind create cluster --name habit-tracker

# Load Docker image into Kind
docker build -t habit-tracker-api:latest .
kind load docker-image habit-tracker-api:latest --name habit-tracker

# Deploy to Kind
kubectl apply -f k8s/

# Check deployment
kubectl get deployments
kubectl get pods
kubectl logs -f deployment/habit-tracker-api

# Port forward to access
kubectl port-forward svc/habit-tracker-api 8000:8000

# Cleanup
kind delete cluster --name habit-tracker
```

### Kubernetes Manifests

- [deployment.yaml](k8s/deployment.yaml) - API deployment with health probes
- [service.yaml](k8s/service.yaml) - ClusterIP service
- [postgres.yaml](k8s/postgres.yaml) - PostgreSQL StatefulSet with persistence
- [configmap.yaml](k8s/configmap.yaml) - Environment configuration

Features:
- Resource limits: 512Mi memory, 500m CPU
- Readiness probe: `pg_isready` every 5s
- Liveness probe: `pg_isready` every 10s
- Image pull policy: IfNotPresent (for Kind)

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci-cd.yml`):

1. **Lint** - flake8 code quality checks
2. **Test** - Unit & integration tests (pytest)
3. **Build** - Docker image build and push
4. **Deploy & E2E** - Deploy to Kind, run Playwright E2E tests
5. **Smoke Test** - API health and basic functionality
6. **Load Test** - k6 performance test (50 VUs, 5min)

All jobs complete within timeout constraints (15 min for E2E, 10 min for load test).

## Project Structure

```
.
├── src/
│   ├── main.py              # FastAPI app, routes
│   ├── models.py            # SQLAlchemy ORM models
│   ├── database.py          # Database configuration
│   ├── auth.py              # JWT & password hashing
│   └── s3.py                # S3/LocalStack avatar uploads
├── templates/               # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html           # Welcome/landing page
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html       # Habit list
│   ├── create_habit.html
│   └── habit_detail.html
├── static/                  # CSS & JavaScript
│   ├── style.css
│   └── app.js
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_unit_auth.py    # Unit tests
│   ├── factories.py         # Factory Boy definitions
│   ├── integration/         # Integration tests
│   ├── e2e/                 # Playwright E2E tests
│   │   ├── conftest.py
│   │   ├── test_e2e.py      # API integration tests
│   │   └── test_e2e_playwright.py  # Browser automation
│   └── testcontainers/      # Isolated DB tests
├── perf/                    # Performance tests
│   ├── smoke-test.js
│   └── load-test.js
├── k8s/                     # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── postgres.yaml
│   └── configmap.yaml
├── .github/workflows/       # CI/CD pipeline
├── docker-compose.yml       # Local dev environment
├── Dockerfile
└── requirements.txt
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (vanilla) |
| **Backend** | FastAPI (Python 3.11) |
| **Database** | PostgreSQL 16 |
| **Testing** | pytest, Factory Boy, Playwright, k6 |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker, Docker Compose |
| **Orchestration** | Kubernetes |
| **Monitoring** | Prometheus, Grafana, OpenTelemetry, Jaeger |
| **Cloud Services** | AWS S3 (LocalStack in dev) |

## Environment Variables

See `.env.example` for all configuration options:

```bash
# Core
DATABASE_URL=postgresql://user:password@db:5432/habits
API_PORT=8000
DEBUG=False

# Auth
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# S3
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
S3_BUCKET=habits
S3_ENDPOINT_URL=http://localstack:4566  # or AWS S3 in production

# Monitoring
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317

# Testing
API_URL=http://localhost:8001
```

## Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# Edit src/, templates/, static/, tests/

# 3. Run tests locally
docker-compose up -d
pytest tests/ -v
pytest tests/e2e/ -v

# 4. Run linting
flake8 src/ tests/

# 5. Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature

# 6. Create PR
# GitHub Actions will automatically:
# - Run linting
# - Run all tests
# - Build Docker image
# - Deploy to Kind cluster
# - Run E2E and load tests
```

## Performance Baseline

From k6 load testing (50 VUs, 5 minutes):

- **p95 Latency**: ~150ms
- **p99 Latency**: ~300ms
- **Requests/sec**: ~80-120 RPS
- **Error Rate**: <5%
- **Success Rate**: >95%

## Troubleshooting

### Docker Compose Issues

```bash
# View all logs
docker-compose logs -f

# Restart API service
docker-compose restart api

# Rebuild images
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

### E2E Tests Failing

```bash
# Ensure API is responding
curl http://localhost:8001/health

# Run tests with verbose output
pytest tests/e2e/ -v -s

# Run in headed mode to see browser
pytest tests/e2e/test_e2e_playwright.py::TestUserRegistrationE2E -v --headed
```

## Contributing

1. Ensure code passes flake8: `flake8 src/ tests/`
2. Write tests for new features
3. Maintain test coverage >70%: `pytest --cov=src`
4. All GitHub Actions jobs must pass

## License

This is a university course assignment for "Bulut Mimarilerinde Test Mühendisliği"

## Authors

- **Student**: Kulo (mertbaytas@gmail.com)
- **Course**: Cloud Architectures & Test Engineering
- **University**: [Institution Name]
- **Date**: May 2026

## Course Requirements Fulfillment

This project fulfills the following course requirements:

| Requirement | Status | Details |
|-------------|--------|---------|
| API Development | ✅ | 8 endpoints, SQLAlchemy ORM, PostgreSQL |
| Unit Testing | ✅ | 12 unit tests (auth, password hashing, JWT) |
| Integration Testing | ✅ | 28 integration tests (fixtures, factories) |
| E2E Testing | ✅ | 6 Playwright scenarios covering full workflows |
| Code Quality | ✅ | 100% flake8 compliant |
| Test Coverage | ✅ | 78.54% code coverage |
| Docker | ✅ | docker-compose with 5+ services |
| Kubernetes | ✅ | Deployments, services, probes, ConfigMap |
| CI/CD | ✅ | GitHub Actions with 6 jobs |
| Performance Testing | ✅ | k6 smoke and load tests |
| Monitoring | ✅ | Prometheus, Grafana, Jaeger |
| Frontend | ✅ | HTML/CSS/JS (no frameworks) |
| Web UI | ✅ | 6 pages: register, login, dashboard, create, detail |

---

**Questions?** See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for deeper technical details, or [SETUP.md](docs/SETUP.md) for step-by-step configuration.
