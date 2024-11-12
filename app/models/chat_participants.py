from sqlalchemy import Table, Column, Integer, ForeignKey
from ..database import Base

chat_participants = Table(
    'chat_participants', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('chat_id', Integer, ForeignKey('chats.id'))
)
