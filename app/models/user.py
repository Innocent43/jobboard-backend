from datetime import datetime
import enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import DateTime,String,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database.base import Base


class UserRole(str, enum.Enum):
    EMPLOYER = "employer"
    JOB_SEEKER = "job_seeker"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255),unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.JOB_SEEKER)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    jobs: Mapped[list["Job"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="applicant", cascade="all, delete-orphan")