from pydantic import BaseModel

class AdminStats(BaseModel):
    total_users: int
    employers: int
    job_seekers: int
    total_jobs: int
    open_jobs: int
    total_applications: int
