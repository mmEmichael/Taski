"""Подключение к БД — engine, сессии и dependency для FastAPI."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """Dependency: выдаёт сессию БД, закрывает после завершения."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
