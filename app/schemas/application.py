from datetime import datetime
from pydantic import BaseModel,ConfigDict
from app.schemas.job import JobRead

class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationRead(BaseModel):
    id: int
    status: str
    created_at: datetime
    user_id: int
    job_id: int
    job: JobRead

    model_config = ConfigDict(from_attributes=True)


class ApplicationUpdate(BaseModel):
    status: str

    