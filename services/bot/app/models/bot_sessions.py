"""Модель пользователя — ORM для таблицы users."""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func

from . import Base

class BotToken(Base):
    __tablename__ = "bot_tokens"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    server_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)