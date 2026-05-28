# Architecture Documentation

Habit Tracker API - Complete System Architecture

## System Overview

The Habit Tracker is a full-stack web application designed to help users manage and track daily habits. The system is built with a focus on testing, scalability, and cloud-native deployment.

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                   (HTML5, CSS3, JavaScript)                      │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTP(S)
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│  - REST API endpoints (8 routes)                                │
│  - JWT authentication & authorization                           │
│  - Request validation & error handling                          │
│  - OpenTelemetry instrumentation                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ↓                 ↓
┌──────────────────┐  ┌──────────────────┐
│   PostgreSQL     │  │  AWS S3/LocalStack
│   - Users table  │  │  - Avatar uploads│
│   - Habits table │  │                  │
│   - Logs table   │  └──────────────────┘
└──────────────────┘

        Observability
        ↓
┌──────────────────────────────────────────┐
│  - Prometheus (metrics)                  │
│  - Grafana (dashboards)                  │
│  - Jaeger (distributed tracing)          │
│  - OpenTelemetry (instrumentation)       │
└──────────────────────────────────────────┘
```

## Detailed Architecture

### 1. Frontend Layer

**Technology**: HTML5, CSS3, JavaScript (Vanilla - no frameworks)

**Pages**:
- `index.html` - Welcome/landing page with gradient background
- `register.html` - User registration form
- `login.html` - User login form (JWT token to localStorage)
- `dashboard.html` - Habit list, create habit button
- `create_habit.html` - Form to create new habit
- `habit_detail.html` - Single habit view with track/edit/delete

**Styling**:
- Responsive CSS with mobile-first design
- CSS Grid for layouts
- Flexbox for components
- Dark theme compatible

**JavaScript (static/app.js)**:
```javascript
// Key functions:
- getToken()              // Retrieve JWT from localStorage
- setToken(token)         // Store JWT in localStorage
- logout()                // Clear token and redirect
- apiCall(method, url, body) // Helper with Authorization header
```

Authentication Flow:
1. User submits login form → JavaScript → `fetch("/login", ...)`
2. API returns JWT token in response
3. JavaScript stores in `localStorage.auth_token`
4. Subsequent requests include: `Authorization: Bearer {token}`

### 2. Backend Layer

**Framework**: FastAPI (Python 3.11 async web framework)

**Core Components**:

#### a) Application (`src/main.py`)
```python
FastAPI()
├── Routes (8 endpoints)
├── Middleware
│   ├── CORS (allow all origins)
│   ├── OTEL tracing
│   └── Error handlers
├── Startup/Shutdown
│   └── Database initialization
└── Static/Template serving
    ├── /static (CSS, JS)
    └── /templates (HTML via Jinja2)
```

**Endpoints**:
| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| GET | / | No | Serve index.html |
| POST | /register | No | Register new user |
| POST | /login | No | Authenticate & get JWT |
| GET | /health | No | Health check (K8s liveness) |
| GET | /metrics | No | Prometheus metrics export |
| GET | /habits | Yes | List user's habits |
| POST | /habits | Yes | Create habit |
| GET | /habits/{id} | Yes | Get habit with logs |
| PATCH | /habits/{id} | Yes | Update habit |
| DELETE | /habits/{id} | Yes | Delete habit |
| POST | /habits/{id}/track | Yes | Log habit completion |
| GET | /habits/{id}/streak | Yes | Calculate current streak |
| POST | /users/{id}/avatar | Yes | Upload avatar to S3 |
| GET | /users/{id}/avatar | Yes | Download avatar from S3 |

#### b) Authentication (`src/auth.py`)
```
password → hash_password() → bcrypt hash (stored in DB)
                ↓
verify_password(plain, hashed) → True/False

JWT Token Generation:
user_id → create_access_token() → JWT (exp: 30 min)
                ↓
verify_token(token) → Extract & verify payload → user_id
```

Key Functions:
- `hash_password(password)` - bcrypt hashing with salt
- `verify_password(plain, hashed)` - Constant-time comparison
- `create_access_token(user_id)` - Create JWT with expiration
- `verify_token(token)` - Validate & extract user_id from JWT

#### c) Database (`src/database.py`)
```
SQLAlchemy ORM
    ↓
PostgreSQL Connection Pool (5-20 connections)
    ↓
Engine & Session Management
```

Connection String: `postgresql://user:password@host:5432/habits`

Features:
- Connection pooling (NullPool for testing, QueuePool for production)
- Lazy session creation
- Transactional integrity

#### d) Models (`src/models.py`)

**User Model**:
```python
class User(Base):
    id: int (PK)
    username: str (unique, indexed)
    password_hash: str (bcrypt)
    created_at: datetime
    
    Relationships:
    └── habits: List[Habit]
```

**Habit Model**:
```python
class Habit(Base):
    id: int (PK)
    user_id: int (FK → User)
    name: str
    description: str
    goal_days_per_week: int
    created_at: datetime
    updated_at: datetime
    
    Relationships:
    ├── user: User
    └── logs: List[HabitLog]
```

**HabitLog Model**:
```python
class HabitLog(Base):
    id: int (PK)
    habit_id: int (FK → Habit)
    done: bool
    duration: int (minutes, optional)
    mood: int (1-5 scale, optional)
    notes: str (optional)
    logged_at: datetime
    
    Relationships:
    └── habit: Habit
```

### 3. Data Layer

**Database**: PostgreSQL 16

**Schema**:
```sql
users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
)

habits (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  goal_days_per_week INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

habit_logs (
  id SERIAL PRIMARY KEY,
  habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
  done BOOLEAN DEFAULT FALSE,
  duration INTEGER,
  mood INTEGER,
  notes TEXT,
  logged_at TIMESTAMP DEFAULT NOW()
)

CREATE INDEX idx_habits_user_id ON habits(user_id);
CREATE INDEX idx_logs_habit_id ON habit_logs(habit_id);
```

**Initialization**: Tables created automatically on app startup via SQLAlchemy `Base.metadata.create_all()`

### 4. External Integrations

#### AWS S3 (Avatar Upload)
```
User Browser
    ↓ (multipart/form-data)
FastAPI /users/{id}/avatar (POST)
    ↓
boto3 client
    ↓
S3 bucket (or LocalStack in dev)
    ↓
stored as: s3://habits-bucket/{user_id}/avatar.jpg
```

Return: `GET /users/{id}/avatar` → S3 pre-signed URL or file stream

### 5. Testing Architecture

#### Unit Tests (12 tests)
- Location: `tests/test_unit_auth.py`
- Focus: Isolated functions (password hashing, JWT)
- Fixtures: None (pure functions)
- Speed: ~1 second

```
test_hash_password_not_plain()
test_verify_correct_password()
test_verify_wrong_password()
test_same_password_different_hash()
test_create_token_format()
test_verify_valid_token()
test_verify_invalid_token()
test_verify_corrupted_token()
test_verify_different_user_ids()
```

#### Integration Tests (28 tests)
- Location: `tests/integration/` + `tests/testcontainers/`
- Focus: Database interactions, API endpoints, relationships
- Fixtures: TestClient, database session, Factory Boy
- Speed: ~5 seconds

```
Fixture Flow:
db fixture
    ↓
override_get_db() (dependency injection)
    ↓
TestClient(app) (in-process)
    ↓ (no real HTTP)
API routes directly
    ↓
Database transaction (rollback after test)
```

#### E2E Tests (15 tests)

**API Integration Tests** (`tests/e2e/test_e2e.py`):
- 12 tests using `requests` library
- Real HTTP requests to running API server
- Scenarios: register, login, create, track, update, delete, errors
- Speed: ~8 seconds (external network)

**Browser Automation Tests** (`tests/e2e/test_e2e_playwright.py`):
- 6 tests using Playwright (Chromium)
- Real browser interactions
- Scenarios: full user workflows through UI
- Speed: ~30 seconds (browser startup + interactions)

```
Playwright Test Flow:
Page (Chrome browser)
    ↓
User interactions (click, fill, select)
    ↓
JavaScript execution (localStorage, form submit)
    ↓
HTTP requests to API
    ↓
Database changes
    ↓
Page assertions (text visible, URL changed)
```

#### Performance Tests (k6 JavaScript)
- Smoke test: 1 VU, 30s (sanity check)
- Load test: 50 VUs, 5 minutes (sustained load)
- Metrics tracked: p95/p99 latency, error rate, throughput

### 6. CI/CD Pipeline (GitHub Actions)

Workflow: `.github/workflows/ci-cd.yml`

```
Event: push to main
    ↓
┌─ Lint (flake8)
│   - Check code quality
│   - Block on errors
│
├─ Test (pytest)
│   - Unit & integration tests
│   - Coverage check (>70%)
│   - Runs in matrix: Python 3.11
│
├─ Build (Docker)
│   - docker build
│   - docker tag
│   - docker push (if needed)
│
├─ Deploy & E2E
│   - Create Kind cluster
│   - Apply K8s manifests
│   - Run Playwright E2E tests
│   - Verify deployment healthy
│
├─ Smoke Test
│   - API health check
│   - /health endpoint
│   - /metrics endpoint
│
└─ Load Test
    - k6 with 50 VUs
    - Verify p95 < threshold
    - Check error rate < 5%

Total Time: ~15-20 minutes
```

Job Dependencies:
```
lint ─┐
      ├─ test ─┐
build ─┤        ├─ deploy-and-test ─┬─ smoke-test ─ load-test
       │        │
       └────────┘
```

### 7. Containerization

#### Docker Compose (Local Development)
```yaml
Services:
├── api
│   ├── Image: Python 3.11
│   ├── Port: 8001 (host) → 8000 (container)
│   ├── Volumes: ./templates, ./static (live reload)
│   ├── Environment: DATABASE_URL, SECRET_KEY
│   └── Depends on: db
│
├── db (PostgreSQL)
│   ├── Image: postgres:16
│   ├── Port: 5432
│   ├── Volumes: postgres_data
│   └── Environment: POSTGRES_PASSWORD
│
├── localstack (AWS S3 emulation)
│   ├── Port: 4566
│   └── Creates: habits bucket
│
├── prometheus
│   ├── Port: 9090
│   └── Scrapes: localhost:8000/metrics
│
├── grafana
│   ├── Port: 3000
│   └── Datasource: Prometheus
│
└── jaeger
    ├── Port: 16686 (UI)
    ├── Port: 4317 (OTLP receiver)
    └── Stores: traces in memory
```

Volume Mounts:
```
Host                           Container
./templates     ↔             /app/templates
./static        ↔             /app/static
postgres_data   ↔             /var/lib/postgresql/data
```

#### Dockerfile (Production)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ src/
COPY templates/ templates/
COPY static/ static/
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8. Kubernetes Deployment

**Cluster**: Kind (Kubernetes in Docker) for local testing

**Manifests**:

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: habit-tracker-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: habit-tracker-api
  template:
    metadata:
      labels:
        app: habit-tracker-api
    spec:
      containers:
      - name: api
        image: habit-tracker-api:latest
        ports:
        - containerPort: 8000
        
        # Resource Management
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # Health Checks
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 5
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        
        # Environment
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database-url
        - name: API_PORT
          value: "8000"
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: habit-tracker-api
spec:
  type: ClusterIP
  selector:
    app: habit-tracker-api
  ports:
  - port: 8000
    targetPort: 8000
```

#### postgres.yaml (StatefulSet)
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16
        ports:
        - containerPort: 5432
        
        # Health Checks
        readinessProbe:
          exec:
            command: ["pg_isready", "-U", "user"]
          initialDelaySeconds: 15
          periodSeconds: 5
        
        livenessProbe:
          exec:
            command: ["pg_isready", "-U", "user"]
          initialDelaySeconds: 30
          periodSeconds: 10
        
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

**Deployment Architecture**:
```
┌─ Node ─────────────────────────┐
│  ┌─────────────────────────┐   │
│  │ Pod: habit-tracker-api  │   │
│  │ - Container: FastAPI    │   │
│  │ - Port 8000             │   │
│  │ - Memory: 256-512Mi     │   │
│  │ - CPU: 250m-500m        │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │ Pod: postgres           │   │
│  │ - Container: PostgreSQL │   │
│  │ - Port 5432             │   │
│  │ - PersistentVolume: 1Gi │   │
│  └─────────────────────────┘   │
└────────────────────────────────┘
         ↓
    Service (ClusterIP:8000)
         ↓
    External Access (port-forward)
```

### 9. Observability

#### Metrics (Prometheus)

Application exports metrics at `/metrics` endpoint:

```
# Counter (incremental)
habit_tracker_requests_total{method="POST", endpoint="/login", status="200"}

# Histogram (latency distribution)
habit_tracker_request_duration_seconds_bucket{endpoint="/habits", le="0.5"}

# Gauge (current value)
habit_tracker_active_users

# Gauge (database pool)
sqlalchemy_pool_size{pool_name="default"}
sqlalchemy_pool_checkedout{pool_name="default"}
```

Configuration:
```
Prometheus scrape interval: 15s
Database metrics: Connection pool status
Request metrics: Method, endpoint, status code, duration
```

#### Distributed Tracing (Jaeger + OpenTelemetry)

All requests traced with:
```
Request ID (span ID)
    ↓
FastAPI route
    ↓
Database query (SQLAlchemy instrumentation)
    ↓
External service (S3 call if applicable)
    ↓
Response (status code + duration)

Trace Attributes:
- http.method
- http.url
- http.status_code
- db.statement (SQL)
- db.rows_affected
```

Example trace:
```
POST /login (1000ms total)
├── auth.verify_password (50ms)
├── database.query (100ms)
├── jwt.create_token (10ms)
└── http.response (5ms)
```

Access Jaeger UI: http://localhost:16686

#### Logging

Application logs to stdout (Docker Compose):
```
2026-05-28 10:00:00 | INFO | User registered: user_123
2026-05-28 10:00:01 | INFO | Habit created: habit_456
2026-05-28 10:00:02 | INFO | Habit tracked: log_789
```

View logs:
```bash
docker-compose logs -f api
kubectl logs -f deployment/habit-tracker-api
```

### 10. Security Architecture

#### Authentication Flow
```
Client                          Server
    │                              │
    ├─ POST /login ────────────→  │
    │ {username, password}         │
    │                              │ verify_password()
    │                              │ create_access_token()
    │  ← {access_token} ──────────│
    │                              │
    │ (store in localStorage)      │
    │                              │
    ├─ GET /habits ─────────────→ │
    │ Authorization: Bearer TOKEN  │
    │                              │ verify_token()
    │  ← [habits] ───────────────│
```

#### Authorization
```
Every protected route requires:
1. Authorization header with Bearer token
2. Token validation (signature, expiration)
3. User isolation (can only access own habits)
```

Dependency injection:
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    return user_id

@app.get("/habits")
async def list_habits(user_id: int = Depends(get_current_user)):
    return db.query(Habit).filter(Habit.user_id == user_id).all()
```

#### Password Security
```
Plain Password
    ↓
bcrypt.hashpw() [salt + hash]
    ↓
Stored in database (non-reversible)
    ↓
verify_password(): bcrypt.checkpw()
    ↓
True / False (constant-time comparison)
```

### 11. Error Handling

HTTP Status Codes:
```
200 OK              - Successful request
201 Created         - Resource created
204 No Content      - Successful delete
400 Bad Request     - Invalid input
401 Unauthorized    - Missing/invalid auth
403 Forbidden       - Auth valid but unauthorized
404 Not Found       - Resource doesn't exist
500 Server Error    - Unexpected error
```

Example Error Response:
```json
{
  "detail": "Invalid credentials"
}
```

Exception Handling:
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

---

## Performance Characteristics

### Baseline (Single Instance, PostgreSQL)
- **Throughput**: 80-120 RPS (requests per second)
- **p95 Latency**: ~150ms
- **p99 Latency**: ~300ms
- **Database**: 5-20 connection pool
- **Memory**: 256-512Mi (Kubernetes limits)
- **CPU**: 250m-500m (Kubernetes limits)

### Bottlenecks
- Database query time (indexes on user_id, habit_id)
- Bcrypt hashing (intentionally slow for security)
- S3 avatar uploads (network I/O)

### Optimization Opportunities
- Add Redis caching for habit lists
- Implement pagination for large datasets
- Use async S3 uploads
- Database read replicas for scaling

---

## Deployment Workflows

### Local Development
```bash
docker-compose up -d
# Development on http://localhost:8001
```

### Testing
```bash
pytest tests/ -v                          # Unit + Integration
pytest tests/e2e/ -v                      # E2E tests
k6 run perf/load-test.js                  # Performance tests
```

### Kind Cluster (Local Kubernetes)
```bash
kind create cluster
kubectl apply -f k8s/
kubectl port-forward svc/habit-tracker-api 8000:8000
```

### GitHub Actions CI/CD
```
git push → GitHub Actions → Lint → Test → Build → Deploy → E2E → Smoke → Load
```

---

## Future Improvements (Not in Scope for University Course)

1. **High Availability**
   - Multi-replica deployment
   - Database replication
   - Load balancer

2. **Security Hardening**
   - Rate limiting
   - API key authentication
   - HTTPS/TLS enforcement
   - Input validation

3. **Performance**
   - Redis caching layer
   - Pagination for large datasets
   - Async file uploads
   - Database query optimization

4. **Features**
   - Habit reminders (push notifications)
   - Social sharing
   - Analytics dashboard
   - Goal recommendations

5. **Operations**
   - Helm charts for K8s
   - Infrastructure as Code (Terraform)
   - Multi-region deployment
   - Disaster recovery plan

---

**See README.md for quick start and testing instructions.**
