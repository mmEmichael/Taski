"""API пользователей — регистрация, логин, информация."""
from fastapi import APIRouter, Depends
from sqlalchemy import insert
from sqlalchemy.orm import Session


from app.api.deps import hash_password, verify_password
from app.schemas.user import UserCredentials
from app.models import User
from app.database import get_db

router = APIRouter()


@router.post("/users/register")
async def register_user(credentials: UserCredentials, db: Session = Depends(get_db)):
    """Регистрация нового пользователя."""
    password_hash = hash_password(credentials.password)
    query = insert(User).values(
        username=credentials.username,
        password_hash=password_hash,
        tg_id=credentials.tg_id,
    )
    db.execute(query)
    db.commit()
    return {"message": "User registered successfully"}


@router.post("/user/auth")
async def auth_user(credentials: UserCredentials):
    """Авторизация пользователя."""
    return credentials


@router.get("users/info")
async def get_user_info(credentials: UserCredentials):
    """Получение информации о пользователе."""
    return credentials