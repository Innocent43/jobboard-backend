from fastapi import APIRouter,WebSocket,WebSocketDisconnect,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.schemas.message import MessageRead,ConversationRead
from app.services import message_service,user_service

router:APIRouter=APIRouter(prefix="/messages",tags=["messages"])

class ConnectionManager:
    def __init__(self)->None:
        self.active_connections: dict[int,WebSocket] = {}

    async def connect(self,user_id: int,websocket: WebSocket)->None:
            await websocket.accept()
            self.active_connections[user_id] = websocket

    def disconnect(self,user_id: int)-> None:
         self.active_connections.pop(user_id,None)

    async def send_to_user(self,user_id: int, message: dict)-> None:
         connection = self.active_connections.get(user_id)
         if connection is not None:
              await connection.send_json(message)



manager = ConnectionManager()

@router.websocket("/ws/{other_user_id}")
async def websocket_chat(websocket: WebSocket,other_user_id: int, token: str, db: AsyncSession=Depends(get_db),)->None:
     payload = decode_access_token(token)
     if payload is None:
          await websocket.close(code=1008)
          return

     email = payload.get("sub")
     current_user = await user_service.authenticate_user_by_email(db,email)
     if current_user is None:
          await websocket.close(code=1008)
          return
     conversation = await message_service.get_or_create_conversation(db,current_user.id,other_user_id)
     await manager.connect(current_user.id,websocket)

     try:
          while True:
               data = await websocket.receive_json()
               content = data.get("content","")
               
               message = await message_service.create_message(db,conversation.id,current_user.id,content)

               payload_out = {
                    "id": message.id,
                    "conversation": message.conversation_id,
                    "sender_id": message.sender_id,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
               }

               await manager.send_to_user(current_user.id,payload_out)
               await manager.send_to_user(other_user_id,payload_out)
     except WebSocketDisconnect:
          manager.disconnect(current_user.id)
