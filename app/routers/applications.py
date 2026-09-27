from fastapi import APIRouter,Depends,HTTPException,status
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.application import ApplicationCreate,ApplicationRead,ApplicationUpdate
from app.services import application_service
from app.dependencies.auth import get_current_user,require_role
from app.models.user import User,UserRole

router = APIRouter(prefix="/applications",tags=["applications"])

@router.post("/",response_model=ApplicationRead,status_code=status.HTTP_201_CREATED)
async def apply_to_job(app_data: ApplicationCreate,current_user: User = Depends(require_role(UserRole.JOB_SEEKER)), db: AsyncSession = Depends(get_db))-> ApplicationRead:
    try:
        return await application_service.create_application(db,app_data,current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/mine", response_model=list[ApplicationRead])
async def get_my_applications(current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db))->list[ApplicationRead]:
    return await application_service.get_applications_by_user(db,current_user.id)

@router.get("/{application_id}",response_model=ApplicationRead)
async def get_application(application_id: int, db: AsyncSession=Depends(get_db)) ->ApplicationRead:
    application = await application_service.get_application_by_id(db,application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Application not found")

    return application

@router.get("/", response_model=list[ApplicationRead])
async def list_applications(db: AsyncSession = Depends(get_db)) -> list[ApplicationRead]:
    return await application_service.get_applications(db)

@router.patch("/{application_id}",response_model=ApplicationRead)
async def update_application(application_id,update_data: ApplicationUpdate, db:AsyncSession = Depends(get_db)) -> ApplicationRead:
    application = await application_service.get_application_by_id(db,application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Application not found")
    return await application_service.update_application_status(db,application,update_data.status)

@router.delete("/{application_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(application_id: int, db: AsyncSession =Depends(get_db)) -> None:
    application = await application_service.get_application_by_id(db,application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Application Not Found")
    await application_service.delete_application(db,application)