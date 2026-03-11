import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import BotToken

def get_session_by_tg_id(db: Session, tg_id: int):
    return db.query(BotToken).filter(BotToken.tg_id == tg_id).one_or_none()

def save_token(
    db: Session,
    tg_id: int,
    token: str,
) -> BotToken:
    session = get_session_by_tg_id(db, tg_id)
    if session is None:
        session = BotToken(
            tg_id=tg_id,
            server_token=token,
        )
        db.add(session)
    else:
        session.server_token = token

    db.commit()
    db.refresh(session)
    return session

def get_valid_token(db: Session, tg_id: int) -> str | None:
    session = get_session_by_tg_id(db, tg_id)
    if not session:
        return None
    #if session.expires_at and session.expires_at <= datetime.utcnow():
        #return None
    return session.server_token
