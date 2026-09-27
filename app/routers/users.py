from fastapi import APIRouter,Depends,HTTPException,status
# from sqlalchemy.orm import Session

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.user import UserCreate,UserRead
from app.services import user_service
from app.dependencies.auth import get_current_user
from app.schemas.user import UserUpdate
from app.models.user import User
from fastapi import BackgroundTasks
import logging


router: APIRouter = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)
def send_welcome_notification(email: str)->None:
    logger.info(f"Welcome notification sent to {email}")

@router.post("/",response_model=UserRead,status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate,background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)) -> UserRead:
    try:
        new_user =await user_service.create_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))
    background_tasks.add_task(send_welcome_notification, new_user.email)
    return new_user

@router.get("/me",response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user))-> UserRead:
    return current_user

@router.patch("/me",response_model=UserRead)
async def update_me(update_data: UserUpdate,current_user: User = Depends(get_current_user),db:AsyncSession=Depends(get_db))->UserRead:
    changes = update_data.model_dump(exclude_unset=True)
    return await user_service.update_user(db,current_user,changes)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: User = Depends(get_current_user),db:AsyncSession=Depends(get_db),)-> None:
    await user_service.delete_user(db,current_user)

@router.get("/{user_id}",response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db))-> UserRead:
    user = await user_service.get_user_by_id(db,user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/",response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserRead]:
    return await user_service.get_users(db)