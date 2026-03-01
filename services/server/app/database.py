from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import db_url

engine = create_engine(
    db_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
