from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.db_models import Base
from typing import Generator

# PostgreSQL doesn't need check_same_thread like SQLite
engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300     # Recreate connections every 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Call this to create tables

def init_db():
    print("[init_db] Starting DB initialization...")
    Base.metadata.create_all(bind=engine)
    print("[init_db] DB initialization complete.")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
