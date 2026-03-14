import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Берём строку подключения из .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Put it into .env and export it or load via python-dotenv.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # проверяет соединение перед использованием
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ping_db() -> bool:
    """Быстрая проверка соединения."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
