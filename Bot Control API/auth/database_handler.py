from sqlalchemy.orm import Session, sessionmaker
from passlib.context import CryptContext
from model import models, schemas
import random
import string
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# password encryption
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# check out users
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, brain_id=user.brain_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_bot(db: Session, bot: schemas.BotCreate):
    container_id = generate_key(50)
    create_time = datetime.datetime
    if get_user(db, bot.owner_id):
        db_bot = models.Bot(**bot, container_id=container_id)
        db.add(db_bot)
        db.commit()
        db.refresh(db_bot)
        return db_bot
    else:
        return None

def generate_key(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_bot_from_email(db: Session, email: str):
    user = get_user_by_email(db, email=email)
    bot = db.query(models.Bot).filter(models.Bot.owner_id == user.id).first()
    if not bot:
        return False
    if bot.request == 0:
        return False
    return bot

def delete_user(db:sessionmaker, email:str):
    user = get_user_by_email(db, email=email)
    try:
        db.query(models.Bot).filter(models.Bot.owner_id == user.id).delete()
        db.query(models.User).filter(models.User.email == email).delete()
        db.commit()
        return True
    except:
        return False
    
def delete_bot(db:sessionmaker, container_id:str):
    try:
        
        db.query(models.Bot).filter(models.Bot.container_id == container_id).delete()
        db.commit()
        return True
    except:
        return False