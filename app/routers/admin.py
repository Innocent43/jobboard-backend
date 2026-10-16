from fastapi import APIRouter,Depends,HTTPException,Query,status

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user,require_role
from app.models.user import UserRole,User
from app.schemas.admin import AdminStats
from app.schemas.job import JobRead
from app.schemas.user import UserRead
from app.services import admin_service,job_service,user_service


router:APIRouter=APIRouter(prefix="/admin",tags=["admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])


@router.get("/stats", response_model=AdminStats)
async def get_stats(db: AsyncSession = Depends(get_db))->AdminStats:
    return await admin_service.get_stats(db)


@router.get("/users", response_model=list[UserRead])
async def list_users(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db))-> list[UserRead]:
    return await user_service.get_users(db,skip,limit)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_admin: User = Depends(get_current_user), db: AsyncSession=Depends(get_db))->None:
    if user_id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You cannot delete your own admin account")
    
    user = await user_service.get_user_by_id(db,user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    await user_service.delete_user(db,user)


@router.get("/jobs", response_model=list[JobRead])
async def list_jobs(skip: int = Query(0,ge=0), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db))->list[JobRead]:
    return await job_service.get_all_jobs(db,skip,limit)


@router.delete("/jobs/{job_d}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int, db: AsyncSession=Depends(get_db))->None:
    job = await job_service.get_job_by_id(db,job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Job not found")
    await job_service.delete_job(db,job)
