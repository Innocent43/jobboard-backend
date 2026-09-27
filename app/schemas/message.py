from datetime import datetime

from pydantic import BaseModel,ConfigDict

class MessageRead(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationRead(BaseModel):
    id: int
    user_a_id: int
    user_b_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    