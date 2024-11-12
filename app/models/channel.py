from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    admin_id = Column(Integer, ForeignKey('users.id'))

    admin = relationship('User', back_populates='channels')
    members = relationship('User', secondary='channel_members', back_populates='channels')
