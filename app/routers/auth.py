from fastapi import APIRouter,Depends,HTTPException,status
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.database.session import get_db
from app.schemas.auth import LoginRequest,Token
from app.services.user_service import authenticate_user
from app.core.limiter import limiter
from fastapi import Request
import logging

router:APIRouter=APIRouter(prefix="/auth", tags=["auth"])

logger:logging=logging.getLogger(__name__)

@router.post("/login",response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request,form_data: OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)) -> Token:
    user = await authenticate_user(db,form_data.username,form_data.password)
    if user is None:
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect email or password")
    logger.info(f"Successfull login: {user.email}")
    token = create_access_token({"sub": user.email})
    return Token(access_token=token)