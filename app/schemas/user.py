from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict,Field
from app.models.user import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6)
    role: UserRole = UserRole.JOB_SEEKER

class UserRead(UserBase):
    id: int
    created_at: datetime
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None