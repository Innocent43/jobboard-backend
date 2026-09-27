# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.schemas.application import ApplicationCreate

async def create_application(db: AsyncSession,app_data:ApplicationCreate, user_id: int)-> Application:
    result = await db.execute(select(Application).filter(Application.user_id == user_id, Application.job_id == app_data.job_id))
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise ValueError("You already applied to this job")
    new_application = Application(user_id=user_id,job_id=app_data.job_id)
    db.add(new_application)
    await db.commit()
    await db.refresh(new_application)
    return new_application

async def get_application_by_id(db: AsyncSession, application_id: int) -> Application | None:
    result = await db.execute(select(Application).filter(Application.id == application_id))
    return result.scalar_one_or_none()

async def get_applications(db: AsyncSession) -> list[Application]:
    result = await db.execute(select(Application))
    return list(result.scalars().all())


async def update_application_status(db: AsyncSession, application: Application, status: str)-> Application:
    application.status = status
    await db.commit()
    await db.refresh(application)
    return application

async def delete_application(db: AsyncSession, application: Application)-> None:
    await db.delete(application)
    await db.commit()


async def get_applications_by_user(db: AsyncSession, user_id: int)-> list[Application]:
    result = await db.execute(select(Application).options(selectinload(Application.job)).filter(Application.user_id == user_id))
    
    return list(result.scalars().all())



    