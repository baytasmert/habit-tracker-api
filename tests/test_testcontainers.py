"""
Testcontainers ile PostgreSQL entegrasyon testleri.
Gerçek bir PostgreSQL container ayağa kaldırarak test eder.

NOT: Bu testler Docker daemon gerektiren ve Linux/CI ortamında çalışan
testlerdir. Windows'ta psycopg2 encoding sorunu nedeniyle skip edilir.
"""
import os
import sys
import pytest

# Set required env vars BEFORE any src imports (config.py validates at module load)
os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost:5432/habits")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("JAEGER_HOST", "localhost")
os.environ.setdefault("OTEL_TRACES_EXPORTER", "none")
os.environ.setdefault("ENABLE_TRACING", "false")

# Windows'ta psycopg2 hostname encoding sorunu nedeniyle skip
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Testcontainers psycopg2 Windows encoding issue - runs on Linux/CI only"
)

from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.database import Base
from src.main import app
from src.database import get_db


@pytest.fixture(scope="module")
def postgres_container():
    """Testcontainers ile gerçek PostgreSQL container başlat."""
    with PostgresContainer("postgres:16") as pg:
        yield pg


@pytest.fixture(scope="module")
def tc_engine(postgres_container):
    """Testcontainer PostgreSQL'e bağlı SQLAlchemy engine."""
    # Build URL manually to avoid Windows locale encoding issues
    port = postgres_container.get_exposed_port(5432)
    user = postgres_container.POSTGRES_USER
    pwd = postgres_container.POSTGRES_PASSWORD
    db = postgres_container.POSTGRES_DB
    url = f"postgresql://{user}:{pwd}@127.0.0.1:{port}/{db}"
    engine = create_engine(url, connect_args={"connect_timeout": 10})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="module")
def tc_client(tc_engine):
    """Testcontainer DB'ye bağlı FastAPI test client."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=tc_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestContainerDatabase:
    """Test 1: Testcontainers PostgreSQL bağlantısı ve şema oluşturma."""

    def test_database_connection_and_schema(self, tc_engine):
        """
        PostgreSQL container başarıyla başlar, tablo şeması oluşturulur
        ve temel SQL sorguları çalışır.
        """
        with tc_engine.connect() as conn:
            # users tablosu oluşturulmuş mu?
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' ORDER BY table_name"
            ))
            tables = [row[0] for row in result]

        assert "users" in tables, "users tablosu oluşturulmadı"
        assert "habits" in tables, "habits tablosu oluşturulmadı"
        assert "habit_logs" in tables, "habit_logs tablosu oluşturulmadı"

    def test_user_registration_with_real_db(self, tc_client):
        """
        Test 2: Gerçek PostgreSQL container üzerinde kullanıcı kayıt akışı.
        Kullanıcı kaydı → login → JWT token → /me endpoint.
        """
        # Register
        reg = tc_client.post("/register", json={
            "username": "tc_test_user",
            "password": "tc_pass_123"
        })
        assert reg.status_code == 201
        assert reg.json()["username"] == "tc_test_user"
        user_id = reg.json()["id"]

        # Login
        login = tc_client.post("/login", json={
            "username": "tc_test_user",
            "password": "tc_pass_123"
        })
        assert login.status_code == 200
        token = login.json()["access_token"]
        assert token is not None

        # /me endpoint
        me = tc_client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["id"] == user_id

    def test_habit_crud_with_real_db(self, tc_client):
        """
        Test 3: Gerçek PostgreSQL üzerinde Habit CRUD + streak hesaplama.
        Create → Track → Streak → Delete akışını test eder.
        """
        # Register + login
        tc_client.post("/register", json={"username": "tc_habit_user", "password": "pass123"})
        login = tc_client.post("/login", json={"username": "tc_habit_user", "password": "pass123"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Habit oluştur
        habit = tc_client.post("/habits", json={
            "name": "Testcontainer Habit",
            "description": "Gerçek DB testi",
            "goal_days_per_week": 5
        }, headers=headers)
        assert habit.status_code == 201
        habit_id = habit.json()["id"]

        # Tracking ekle (done=True)
        track = tc_client.post(f"/habits/{habit_id}/track", json={
            "done": True,
            "duration": 30,
            "notes": "Testcontainer tracking"
        }, headers=headers)
        assert track.status_code == 201

        # Streak sorgula
        streak = tc_client.get(f"/habits/{habit_id}/streak", headers=headers)
        assert streak.status_code == 200
        assert streak.json()["streak_days"] >= 1

        # Habit sil
        delete = tc_client.delete(f"/habits/{habit_id}", headers=headers)
        assert delete.status_code == 200

        # Silinen habit'i sorgula — 404 beklenir
        get = tc_client.get(f"/habits/{habit_id}", headers=headers)
        assert get.status_code == 404

    def test_data_persistence_across_requests(self, tc_engine, tc_client):
        """
        Test 4: Verinin gerçek PostgreSQL'de persist edildiğini doğrula.
        İki ayrı request arasında veri korunuyor mu?
        """
        # Kayıt ve login
        tc_client.post("/register", json={"username": "persist_user", "password": "pass123"})
        login = tc_client.post("/login", json={"username": "persist_user", "password": "pass123"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3 habit oluştur
        for i in range(3):
            tc_client.post("/habits", json={"name": f"Habit {i}"}, headers=headers)

        # Ayrı bir request'te listele — hepsi görünmeli
        habits = tc_client.get("/habits", headers=headers)
        assert habits.status_code == 200
        assert len(habits.json()) == 3

        # SQLAlchemy ile direkt DB sorgusu — aynı veriyi doğrula
        with tc_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM habits h "
                "JOIN users u ON h.user_id = u.id "
                "WHERE u.username = 'persist_user'"
            ))
            count = result.scalar()
        assert count == 3
