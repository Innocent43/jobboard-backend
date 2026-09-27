from sqlalchemy import select,or_,and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Conversation,Message


async def get_or_create_conversation(db: AsyncSession,user_a_id:int,user_b_id:int)->Conversation:
    result = await db.execute(select(Conversation).filter(or_(and_(Conversation.user_a_id == user_a_id,Conversation.user_b_id == user_b_id),and_(Conversation.user_a_id == user_b_id,Conversation.user_b_id == user_a_id),)))
    conversation = result.scalar_one_or_none()
    if conversation is not None:
        return conversation

    new_conversation = Conversation(user_a_id=user_a_id,user_b_id=user_b_id)
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    return new_conversation



async def create_message(db:AsyncSession,conversation_id:int,sender_id:int,content:str)->Message:
    new_messsage=Message(conversation_id=conversation_id,sender_id=sender_id,content=content)
    db.add(new_messsage)
    await db.commit()
    await db.refresh(new_messsage)
    return new_messsage

async def get_conversation_messages(db:AsyncSession,conversation_id:int)->list[Message]:
    result = await db.execute(select(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at))

    return list(result.scalars().all())

