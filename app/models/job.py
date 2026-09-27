from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.database.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    company: Mapped[str] = mapped_column(String(150))
    location: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    is_open: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    owner: Mapped["User"] = relationship(back_populates="jobs")
    applications: Mapped[list["Application"]]= relationship(back_populates="job",cascade="all, delete-orphan")