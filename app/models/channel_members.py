from sqlalchemy import Table, Column, Integer, ForeignKey
from ..database import Base

channel_members = Table(
    'channel_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('channel_id', Integer, ForeignKey('channels.id'))
)
