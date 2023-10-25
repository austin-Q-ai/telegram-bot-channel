from sqlalchemy.orm import Session, sessionmaker
from passlib.context import CryptContext
from model import models, schemas
from bots.bot_docker import create_docker_run, remove_containers, delete_bot_chat_room

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# password encryption
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# get user form email and id
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

# user sign up
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, brain_api=user.brain_api, video_api=user.video_api)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# create bot
def create_bot(db: Session, bot: schemas.BotCreate, config_path:str, db_path:str):
    exist_bot = db.query(models.Bot).filter(models.Bot.bot_username == bot.bot_username).first()
    if exist_bot:
        return 1
    exist_bot = db.query(models.Bot).filter(models.Bot.bot_token == bot.bot_token).first()
    if exist_bot:
        return 2
    try:
        container_name = bot.bot_username
        container_id = create_docker_run("bot:test", container_name, config_path, db_path)
        db_bot = models.Bot(bot_username=bot.bot_username,
                            bot_token=bot.bot_token,
                            bot_name=bot.bot_name,
                            brain_id=bot.brain_id,
                            video_id=bot.video_id,
                            owner_id=bot.owner_id,
                            container_id=container_id)
        db.add(db_bot)
        db.commit()
        db.refresh(db_bot)
        return db_bot
    except:
        return 0

# get bot info from owner email and bot token
def get_bot_from_email(db: Session, email: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    bot = db.query(models.Bot).filter(models.Bot.owner_id == user.id).first()
    if not bot:
        return False
    return bot

def get_bot_from_token(db: Session, token: str):
    bot = db.query(models.Bot).filter(models.Bot.bot_token == token).first()
    if not bot:
        return False
    else:
        return bot

# user delete
def delete_user(db:sessionmaker, email:str):
    user = get_user_by_email(db, email=email)
    bot = get_bot_from_email(db, email=email)
    if bot is not False:
        remove_containers(bot.container_id)
        delete_bot_chat_room(bot.bot_username, user.brain_api)
    try:
        db.query(models.Bot).filter(models.Bot.owner_id == user.id).delete()
        db.query(models.User).filter(models.User.email == email).delete()
        db.commit()
        return True
    except:
        return False

# bot delete with container id
def delete_bot(db:sessionmaker, container_id:str):
    try:
        db.query(models.Bot).filter(models.Bot.container_id == container_id).delete()
        db.commit()
        return True
    except:
        return False


def users_bots(db:sessionmaker):
    users = db.query(models.User).all()
    result = []
    for user in users:
        each = {}
        each["id"]=user.id
        each["email"] = user.email
        each["brain_api"] = user.brain_api
        each["video_api"] = user.video_api
        each["is_active"] = user.is_active

def bots(db:sessionmaker):
    bots = db.query(models.Bot).all()
    result = []
    for bot in bots:
        each = {}
        each["bot_usernam"] = bot.bot_username
        each["bot_token"] = bot.bot_token
        each["bot_name"] = bot.bot_name
        each["brain_id"] = bot.brain_id
        each["container_id"] = bot.container_id
        user = get_user(bot.owner_id)
        each["email"] = user.email
        each["brain_api"] = user.brain_api
        each["video_api"] = user.video_api
        each["is_active"] = user.is_active
        result.append(each)
    return result