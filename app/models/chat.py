from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Chat, User
from pydantic import BaseModel

router = APIRouter()

class ChatCreate(BaseModel):
    participant_ids: list[int]

@router.post("/")
def create_chat(chat: ChatCreate, db: Session = Depends(get_db)):
    new_chat = Chat()  # Создаем новый чат
    db.add(new_chat)  # Добавляем чат в сессию
    db.commit()  # Сохраняем изменения в БД
    db.refresh(new_chat)  # Обновляем объект

    # Добавляем участников в чат
    for user_id in chat.participant_ids:
        # Логика добавления участников, если она у вас есть
        pass

    return new_chat  # Возвращаем созданный чат
