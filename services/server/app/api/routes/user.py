"""API пользователей — регистрация, логин, информация."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from jwt import encode

from app.api.deps import hash_password, verify_password, get_current_user
from app.schemas.user import UserCredentials
from app.models import User
from app.database import get_db
from app.config import SECRET_KEY

router = APIRouter()


@router.post("/user/register")
async def register_user(credentials: UserCredentials, db: Session = Depends(get_db)):

    password_hash = hash_password(credentials.password)

    stmt = insert(User).values(
        username=credentials.username,
        password_hash=password_hash,
        tg_id=credentials.tg_id
    ).on_conflict_do_nothing(index_elements=["tg_id"])

    db.execute(stmt)
    db.commit()

    return {"message": "ok"}


@router.post("/user/auth")
async def auth_user(
    credentials: UserCredentials, 
    db: Session = Depends(get_db)
    ):
    """Авторизация пользователя."""
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = encode(
        {
            "sub": str(user.id),
            "username": user.username,
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    return {"token": token}


@router.get("/user/info")
async def get_user_info(
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user)
    ):
    """Получение информации о пользователе."""
    user = db.query(User).filter(User.id == user_id).first()
    return {"username": user.username, "tg_id": user.tg_id, "created": user.created_at}