from passlib.context import CryptContext
from jwt import decode, ExpiredSignatureError, DecodeError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import SECRET_KEY
from app.models import User
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хэширование пароля."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(password, hashed_password)

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
    ):
    """Получение текущего пользователя."""
    try:
        decoded_token = decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while validating token",
        )

    user = db.query(User).filter(User.id == int(decoded_token["sub"])).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    return user.id

