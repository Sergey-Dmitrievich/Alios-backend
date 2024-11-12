from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, Chat, Message, Channel
from pydantic import BaseModel
import bcrypt
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
from .models import chat_participants
import bcrypt
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


# Список активных подключений
active_connections: List[WebSocket] = []


router = APIRouter()


@router.websocket("/ws/chat/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: int):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for connection in active_connections:
                await connection.send_text(f"Message from chat {chat_id}: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)




# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Модель для регистрации пользователя
class UserCreate(BaseModel):
    phone_number: str
    name: str
    password: str

# Регистрация нового пользователя


@router.post("/register", response_model=UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        phone_number=user.phone_number,
        name=user.name,
        password_hash=hashed_password.decode('utf-8')
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Остальной код остается без изменений...

# Создание чата
class ChatCreate(BaseModel):
    participant_ids: list

@router.post("/chats", response_model=Chat)
def create_chat(chat: ChatCreate, db: Session = Depends(get_db)):
    new_chat = Chat()
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    for user_id in chat.participant_ids:
        db.execute(chat_participants.insert().values(user_id=user_id, chat_id=new_chat.id))
    db.commit()

    return new_chat


# Модель для создания канала
class ChannelCreate(BaseModel):
    name: str
    admin_id: int

# Создание нового канала
@router.post("/channels", response_model=Channel)
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    new_channel = Channel(
        name=channel.name,
        admin_id=channel.admin_id
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return new_channel

# Получение всех каналов
@router.get("/channels", response_model=List[Channel])
def get_channels(db: Session = Depends(get_db)):
    return db.query(Channel).all()


# Отправка сообщения в чат
class MessageCreate(BaseModel):
    channel_id: int
    content: str

@router.post("/channels/{channel_id}/messages")
def send_channel_message(channel_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    new_message = Message(
        channel_id=channel_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    # Здесь можно добавить логику отправки сообщений через WebSocket
    return new_message


@router.post("/messages", response_model=Message)
def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    new_message = Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message

# WebSocket для чата
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/chat/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(f"Message from chat {chat_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
# Подписка пользователя на канал
@router.post("/channels/{channel_id}/subscribe")
def subscribe_to_channel(channel_id: int, user_id: int, db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if channel is None or user is None:
        raise HTTPException(status_code=404, detail="Channel or User not found")
    
    # Проверка, уже ли пользователь подписан на канал
    if user in channel.members:
        raise HTTPException(status_code=400, detail="User already subscribed to the channel")
    
    channel.members.append(user)
    db.commit()
    return {"message": "User subscribed to channel"}

# Отписка пользователя от канала
@router.post("/channels/{channel_id}/unsubscribe")
def unsubscribe_from_channel(channel_id: int, user_id: int, db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if channel is None or user is None:
        raise HTTPException(status_code=404, detail="Channel or User not found")
    
    # Проверка, подписан ли пользователь на канал
    if user not in channel.members:
        raise HTTPException(status_code=400, detail="User not subscribed to the channel")
    
    channel.members.remove(user)
    db.commit()
    return {"message": "User unsubscribed from channel"}
@router.get("/channels/{channel_id}/messages", response_model=List[Message])
def get_channel_messages(channel_id: int, db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.channel_id == channel_id).all()
