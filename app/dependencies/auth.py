from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme),db: AsyncSession = Depends(get_db))-> User:

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"},)


    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    
    return user

def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user))-> User:
        if current_user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"This action requires {required_role.value} role",)
        return current_user
    return role_checker
