# Fast API
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# Database Model
from model import models, schemas
import auth.database_handler as crud
import auth.jwt_token_handler as token
from model.database import SessionLocal, engine
# docker control functions
import bots.bot_docker as docker_bot
# Main process
import os
import time

from datetime import timedelta
from typing import Annotated
import uvicorn

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sign Up
@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        return login_user(user, db)
    user = crud.create_user(db=db, user=user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token.create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return {
        "id": user.id, 
        "email": user.email,
        "brain_api": user.brain_api ,
        "video_api":user.video_api, 
        "is_active": user.is_active, 
        "access_token": access_token, 
        "token_type": "bearer"
    }

# Delete Users
@app.delete("/users",)
def create_user(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=401, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    if crud.delete_user(db, email=email):
        return {"result":"Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed in deleting user")

# Sign in
@app.post("/logins")
def login_user(user: schemas.Userlogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, email=user.email, password=user.password)
    if db_user is False:
        raise HTTPException(status_code=400, detail="User not found")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token.create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Create Bot key
@app.post("/bot/create", response_model=schemas.Bot)
def create_bot(token_str: Annotated[str, Depends(oauth2_scheme)], bot_info: schemas.BotBase, db: Session = Depends(get_db)):
    # Check user authentication
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=401, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)

    # Check user activation status
    user = crud.get_user_by_email(db, email=email)
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Your account is disabled")
    
    # Checking for bot presence
    bot = crud.get_bot_from_email(db, email=email)
    if bot:
        raise HTTPException(status_code=400, detail="Bot was already created")
    
    bots = schemas.BotCreate(owner_id=user.id,
                            bot_username=bot_info.bot_username,
                            bot_token=bot_info.bot_token,
                            bot_name=bot_info.bot_name,
                            brain_id=bot_info.brain_id,
                            video_id=bot_info.video_id)
    # Create a bot configuration file
    config_path = docker_bot.create_config_env(
        brain_api=user.brain_api,
        video_api=user.video_api,
        brain_id=bot_info.brain_id,
        video_id=bot_info.video_id,
        bot_username=bot_info.bot_username,
        bot_token=bot_info.bot_token,
        bot_name=bot_info.bot_name,
    )
    # Create bot DB file
    db_path = docker_bot.create_bot_db(bot_username=bot_info.bot_username)
    # create bot
    bot = crud.create_bot(db, bot=bots, config_path=config_path, db_path=db_path)
    if bot == 0:
        raise HTTPException(status_code=404, detail="Failed in creating Bot")
    elif bot == 1:
        raise HTTPException(status_code=404, detail="Bot username already exists")
    elif bot == 2:
        raise HTTPException(status_code=404, detail="Bot token already exists")
    status = docker_bot.get_status_Containers(bot.container_id)
    return {
        'id':bot.id, 
        "bot_username":bot.bot_username, 
        "bot_name":bot.bot_name, 
        "brain_id":bot.brain_id,
        "video_id":bot.video_id,
        "container_id":bot.container_id, 
        "is_active":bot.is_active,
        "status":status
    }


# Get info of your bot
@app.get("/bot", response_model=schemas.Bot)
def get_bot_info(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=401, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    bot = crud.get_bot_from_email(db, email=email)
    if bot is False:
        raise HTTPException(status_code=404, detail="Don't have bot")
    status = docker_bot.get_status_Containers(bot.container_id)
    return {
        'id':bot.id, 
        "bot_username":bot.bot_username, 
        "bot_name":bot.bot_name, 
        "brain_id":bot.brain_id,
        "video_id":bot.video_id,
        "container_id":bot.container_id, 
        "is_active":bot.is_active,
        "status":status
    }


@app.post("/bot/start")
def start_bot(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=401, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    bot = crud.get_bot_from_email(db, email=email)
    if bot is False:
        raise HTTPException(status_code=404, detail="Bot not found")
    docker_bot.start_containers(bot.container_id)
    status = docker_bot.get_status_Containers(bot.container_id)
    if status == "running":
        return {"result":"Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed")

@app.post("/bot/stop")
def stop_bot(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=401, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    bot = crud.get_bot_from_email(db, email=email)
    if bot is False:
        raise HTTPException(status_code=404, detail="Bot not found")
    docker_bot.stop_containers(bot.container_id)
    status = docker_bot.get_status_Containers(bot.container_id)
    if status == "exited":
        return {"result":"Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed")

@app.delete("/bot/delete")
def delete_bot(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)): 
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=401, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    bot = crud.get_bot_from_email(db, email=email)
    if bot is False:
        raise HTTPException(status_code=404, detail="Bot not found")
    docker_bot.remove_containers(bot.container_id)
    user = crud.get_user(db, bot.owner_id)
    docker_bot.delete_bot_chat_room(bot.bot_username, user.brain_api)
    status = docker_bot.get_status_Containers(bot.container_id)
    if status == None:
        if crud.delete_bot(db, bot.container_id):
            return {"result":"Successfully"}
        else:
            raise HTTPException(status_code=404, detail="distoryed")
    else:
        raise HTTPException(status_code=404, detail="Failed")


# Recieve the error report from deployed telegram bots
@app.post("/reporter")
def reporter(tg_token: Annotated[str, Depends(oauth2_scheme)], report:schemas.Report, db: Session = Depends(get_db)):
    bot = crud.get_bot_from_token(db, tg_token)
    if not bot:
        raise HTTPException(status_code=404, detail="This bot does not exist")

    log_time = time.ctime()
    split = " =/=/=/=/= "
    log_content = log_time + split + bot.bot_token + split + report.target + split + str(report.status) + split + report.description + "\n"

    with open("bots_log.txt", "a+") as log:
        log.writelines(log_content)
    return {"result":"report successfully"}


@app.post("/admin/bots")
def bots(token_str:Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    if token.decode_access_token(token=token_str) != "admin@mygpt.com":
        raise HTTPException(status_code=404, detail="This bot does not exist")
    bots = crud.bots(db)
    return {"bots":bots}

if __name__ == "__main__":
    #os.remove('clone_voice_source/New_Hero.mp3')
    uvicorn.run(app, host="0.0.0.0", port=8008)