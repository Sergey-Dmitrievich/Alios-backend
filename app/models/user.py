from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Message, Chat
from pydantic import BaseModel
from typing import List

router = APIRouter()

class MessageCreate(BaseModel):
    chat_id: int
    sender_id: int
    content: str

# Создание нового сообщения
@router.post("/messages", response_model=Message)
def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == message.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message = Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message

# Получение сообщений для чата
@router.get("/chats/{chat_id}/messages", response_model=List[Message])
def get_chat_messages(chat_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    return messages
