from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,Text,UniqueConstraint,func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class Conversation(Base):
    __tablename__="conversations"
    __table_args__=(UniqueConstraint("user_a_id","user_b_id", name="uq_conversation_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_a_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    user_b_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation",cascade="all, delete-orphan")



class Message(Base):
    __tablename__="messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")