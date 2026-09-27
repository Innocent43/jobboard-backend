
# from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from app.schemas.job import JobCreate

async def create_job(db: AsyncSession,job_data: JobCreate,owner_id: int)-> Job:
    new_job = Job(
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        description=job_data.description,
        owner_id=owner_id,
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job

async def get_job_by_id(db: AsyncSession,job_id: int) -> Job | None:
    result = await db.execute(select(Job).filter(Job.id == job_id))
    return result.scalar_one_or_none()


async def get_jobs(db: AsyncSession)-> list[Job]:
    result =  await db.execute(select(Job))
    return list(result.scalars().all())


async def update_job(db: AsyncSession, job: Job, update_data: dict) -> Job:
    for field,value in update_data.items():
        setattr(job,field,value)
    await db.commit()
    await db.refresh(job)
    return job


async def delete_job(db: AsyncSession,job:Job)-> None:
    await db.delete(job)
    await db.commit()


async def get_jobs_by_owner(db: AsyncSession,owner_id: int)->list[Job]:
    result = await db.execute(select(Job).filter(Job.owner_id == owner_id))
    return list(result.scalars().all())
