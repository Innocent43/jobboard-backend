from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict,Field
from app.models.user import UserRole
from typing import Literal

PublicRole =Literal["employer", "job_seeker"]

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: PublicRole = "job_seeker"

class UserRead(UserBase):
    id: int
    created_at: datetime
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserSummary(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config=ConfigDict(from_attributes=True)