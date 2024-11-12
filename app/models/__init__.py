from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Table
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
from .user import User
from .channel import Channel
from .chat import Chat
from .message import Message
from .chat_participants import chat_participants
from .channel_members import channel_members


# Ассоциация для участников чата
chat_participants = Table(
    'chat_participants', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('chat_id', Integer, ForeignKey('chats.id'))
)

# Ассоциация для участников канала
channel_members = Table(
    'channel_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('channel_id', Integer, ForeignKey('channels.id'))
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String)
    avatar_url = Column(String)
    password_hash = Column(String)

    chats = relationship('Chat', secondary=chat_participants, back_populates='participants')
    channels = relationship('Channel', secondary=channel_members, back_populates='members')

class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, index=True)
    participants = relationship('User', secondary=chat_participants, back_populates='chats')
    messages = relationship('Message', back_populates='chat')

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('User', back_populates='messages')


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    admin_id = Column(Integer, ForeignKey('users.id'))

    admin = relationship('User', back_populates='channels')
    members = relationship('User', secondary=channel_members, back_populates='channels')
    messages = relationship('ChannelMessage', back_populates='channel')
    channel_members = Table(
    'channel_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('channel_id', Integer, ForeignKey('channels.id'))
)


class ChannelMessage(Base):
    __tablename__ = 'channel_messages'
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    channel = relationship('Channel', back_populates='messages')
    sender = relationship('User', back_populates='channel_messages')
