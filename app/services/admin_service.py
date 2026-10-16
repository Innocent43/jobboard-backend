from sqlalchemy import Select,func,select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.job import Job
from app.models.user import User,UserRole
from app.schemas.admin import AdminStats



async def _count(db: AsyncSession, statement: Select[tuple[int]])->int:
    return await db.scalar(statement) or 0


async def get_stats(db: AsyncSession)->AdminStats:
  return AdminStats(
       total_users = await _count(db, select(func.count(User.id))),
     
         employers = await _count(db,select(func.count(User.id)).where(User.role == UserRole.EMPLOYER)),
     
         job_seekers=await _count(db, select(func.count(User.id)).where(User.role == UserRole.JOB_SEEKER)),
     
         total_jobs = await _count(db,select(func.count(Job.id))),
     
         open_jobs = await _count(db,select(func.count(Job.id)).where(Job.is_open.is_(True))),
     
         total_applications = await _count(db,select(func.count(Application.id))),
  )