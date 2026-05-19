import os                                    # STEP 1: İşletim sistemi
from sqlalchemy import create_engine         # STEP 2: Motor oluştur
from sqlalchemy.orm import sessionmaker, declarative_base  # STEP 2: Fabrika + Şablon

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/habits")  # STEP 3: PostgreSQL URL (Docker'da)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(                 # STEP 5: Bağlantı fabrikası
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()                    # STEP 6: Tablo şablonu

def get_db():                                # STEP 7: Bağlantı yöneticisi
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
