from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str | None = None
    due_at: str | None = None

class TaskUpdate(BaseModel):
    id: int
    title: str | None = None
    description: str | None = None
    status: str | None = None
    due_at: str | None = None

