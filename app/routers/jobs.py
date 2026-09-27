from fastapi import APIRouter,Depends,HTTPException,status
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession 

from app.database.session import get_db
from app.schemas.job import JobCreate,JobUpdate,JobRead
from app.services import job_service
from app.dependencies.auth import get_current_user,require_role
from app.models.user import User,UserRole

router: APIRouter = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/",response_model=JobRead,status_code=status.HTTP_201_CREATED)
async def create_job(job_data: JobCreate, current_user: User = Depends(require_role(UserRole.EMPLOYER)),db: AsyncSession = Depends(get_db)) -> JobRead:
    return await job_service.create_job(db,job_data,current_user.id)


@router.get("/mine",response_model=list[JobRead])
async def get_my_jobs(current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db),)-> list[JobRead]:
    return await job_service.get_jobs_by_owner(db,current_user.id)


@router.get("/{job_id}",response_model=JobRead)
async def get_job(job_id: int,db: AsyncSession = Depends(get_db))-> JobRead:
    job =await job_service.get_job_by_id(db,job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Not Found")
    return job


@router.get("/",response_model=list[JobRead])
async def list_jobs(db: AsyncSession = Depends(get_db)) -> list[JobRead]:
    return await job_service.get_jobs(db)


@router.patch("/{job_id}",response_model=JobRead)
async def patch_job(job_id: int, update_data: JobUpdate,current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> JobRead:
    job = await job_service.get_job_by_id(db,job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Job Not Found")
    if job.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not your job posting")
    
    changes = update_data.model_dump(exclude_unset=True)
    return await job_service.update_job(db,job,changes)


@router.put("/{job_id}",response_model=JobRead)
async def put_job(job_id: int, job_data: JobCreate,current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> JobRead:
    job = await job_service.get_job_by_id(db,job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Job Not Found")
    if job.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not your job listing")
    
    changes = job_data.model_dump()
    return await job_service.update_job(db,job,changes)


@router.delete("/{job_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int,current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)) -> None:
    job = await job_service.get_job_by_id(db,job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Job Not Found")
    if job.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Your Job Listing")
    
    await job_service.delete_job(db,job)