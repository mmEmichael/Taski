from pydantic import BaseModel

class UserCredentials(BaseModel):
    user: str
    password: str
    tg_id: int | None = None