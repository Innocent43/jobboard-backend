
# from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import verify_password


async def create_user(db: AsyncSession,user_data: UserCreate)-> User:
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user is not None:
        raise ValueError("Email already registered")

    new_user = User(
        name = user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).filter(User.id == user_id))

    return result.scalar_one_or_none()


async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return list(result.scalars().all())



async def authenticate_user(db: AsyncSession,email: str, password: str)-> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password,user.hashed_password):
        return None

    return user

async def update_user(db: AsyncSession, user: User, Update_data: dict)-> User:
    for field, value in Update_data.items():
        setattr(user,field,value)
        await db.commit()
        await db.refresh(user)
        return user


async def delete_user(db: AsyncSession, user:User)-> None:
    await db.delete(user)
    await db.commit()


async def authenticate_user_by_email(db: AsyncSession,email: str)-> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()
