from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,String,func,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.database.base import Base


class Application(Base):
    __tablename__ = "applications"
    __table_args__=(UniqueConstraint("user_id","job_id", name="uq_user_job_application"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(50),default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))

    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id",ondelete="CASCADE"))

    applicant: Mapped["User"] = relationship(back_populates="applications")

    job: Mapped["Job"] = relationship(back_populates="applications")