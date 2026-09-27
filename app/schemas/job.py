from datetime import datetime
from pydantic import BaseModel,ConfigDict

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str


class JobCreate(JobBase):
    pass

class JobRead(JobBase):
    id: int
    is_open: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None
    is_open: bool | None = None