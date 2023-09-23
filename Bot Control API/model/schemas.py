from typing import Union
from pydantic import BaseModel
from datetime import datetime

# User 
class UserInit(BaseModel):
    email: str

class UserBase(UserInit):
    brain_id:str

class UserCreate(UserInit):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    bots: list[Bot] = []

    class Config:
        from_attributes = True

# Bot
class BotInit(BaseModel):
    bot_username:str

class BotBase(BotInit):
    bot_token:str
    bot_name:str
    brain_api:str
    video_api:str

class BotCreate(BotBase):
    owner_id:int
   
class Bot(BotBase):
    id: int
    is_active: bool
    container_id: str

    class Config:
        from_attributes = True