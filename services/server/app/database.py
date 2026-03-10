"""Подключение к БД — engine, сессии и dependency для FastAPI."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from .config import DATABASE_URL


logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
logger.info("Создан SQLAlchemy engine для подключения к БД.")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """Dependency: выдаёт сессию БД, закрывает после завершения."""
    db = SessionLocal()
    logger.debug("Открыта сессия БД.")
    try:
        yield db
    finally:
        db.close()
        logger.debug("Сессия БД закрыта.")
