from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    brain_id = Column(int)
    is_active = Column(Boolean, default=True)

    bot = relationship("Bot", back_populates="owner")


class Bot(Base):
    __tablename__ = "bot"

    id = Column(Integer, primary_key=True, index=True)
    bot_username = Column(String, unique=True, index=True)
    bot_token = Column(String, unique=True, index=True)
    bot_name = Column(String)
    brain_api = Column(String)
    video_api = Column(String)
    container_id = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="bot")