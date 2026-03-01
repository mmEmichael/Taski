"""API пользователей — регистрация, логин, информация."""
from fastapi import APIRouter

from ...schemas.user import UserCredentials

router = APIRouter()


@router.post("/users/register")
async def register_user(credentials: UserCredentials):
    """Регистрация нового пользователя."""
    return credentials


@router.post("/user/auth")
async def auth_user(credentials: UserCredentials):
    """Авторизация пользователя."""
    return credentials


@router.get("users/info")
async def get_user_info(credentials: UserCredentials):
    """Получение информации о пользователе."""
    return credentials