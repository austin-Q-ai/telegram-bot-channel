from typing import Union
from pydantic import BaseModel
from datetime import datetime

# Bot
class BotInit(BaseModel):
    bot_username:str
    bot_name:str
    brain_id:str
    video_id:str

class BotBase(BotInit):
    bot_token:str
    
class BotCreate(BotBase):
    owner_id:int
   
class Bot(BotInit):
    id: int
    is_active: bool
    container_id: str
    status:str

    class Config:
        from_attributes = True

# User 
class UserInit(BaseModel):
    email: str

class UserBase(UserInit):
    brain_api:str
    video_api:str

class UserCreate(UserBase):
    password: str    

class User(UserBase):
    id: int
    is_active: bool
    bots: list[Bot] = []

    class Config:
        from_attributes = True

class Userlogin(UserInit):
    password: str

class Report(BaseModel):
    target:str
    status:int
    description:str