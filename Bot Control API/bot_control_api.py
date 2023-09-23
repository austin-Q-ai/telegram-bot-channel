# Fast API
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
# Database Model
from model import models, schemas
import auth.database_handler as crud
import auth.jwt_token_handler as token
from model.database import SessionLocal, engine
# docker control functions
import auth.bot_docker as docker_bot
# Main process
import os
import shutil

from datetime import timedelta
from typing import Annotated
import uvicorn

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sign Up
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


# Sign in
@app.post("/logins/")
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, email=user.email, password=user.password)
    if db_user is False:
        raise HTTPException(status_code=404, detail="User not found")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token.create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Create Bot key
@app.post("/bot/create", response_model=schemas.Bot)
def create_bot(token_str: Annotated[str, Depends(oauth2_scheme)], bot_info: schemas.BotBase, db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    bot = crud.get_bot_from_email(db, email=email)
    if bot:
        raise HTTPException(status_code=400, detail="Bot was already created")
    user = crud.get_user_by_email(db, email=email)
    bot = schemas.BotCreate(owner_id=user.id, **bot_info)
    db_api = crud.create_bot(db, bot=bot)
    if db_api is None:
        raise HTTPException(status_code=404, detail="Failed in creating API key")
    return db_api


# Get API Key
@app.get("/bot/", response_model=schemas.Bot)
def get_bot_info(token_str: Annotated[str, Depends(oauth2_scheme)], user: schemas.UserBase, db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    bot = crud.get_bot_from_email(db, email=email)
    if bot is False:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


@app.post("/bot/start")
def start_bot(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    email = token.decode_access_token_specfic(token=token_str, content_key="bot_id")
    bot = docker_bot.start_bot(bot_id=bot_id)
    if bot is False:
        raise HTTPException(status_code=404, detail="Bot not found")
    raise HTTPException(status_code=200, detail="Bot not found")

@app.post("/bot/stop")
def start_bot(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    email = token.decode_access_token_specfic(token=token_str, content_key="bot_id")
    bot = docker_bot.stop_bot(bot_id=bot_id)
    if bot is False:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

@app.post("/bot/delete")
def start_bot(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)): 
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    container_id = token.decode_access_token_specfic(token=token_str, content_key="container_id")
    docker_bot.remove_bot(container_id=container_id)
    if crud.delete_bot(db, bot_username=bot_username):
        return {"result":"Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed")

# Delete Users
@app.post("/delete/users/",)
def create_user(token_str: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    email = token.decode_access_token(token=token_str)
    if crud.delete_user(db, email=email):
        return {"result":"Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed")


# Delete API
@app.post("/delete/bot/{bot_username}")
def create_user(token_str: Annotated[str, Depends(oauth2_scheme)], bot_username:str, db: Session = Depends(get_db)):
    if not token.verify_token(token=token_str):
        raise HTTPException(status_code=404, detail="User don't sign in")
    if crud.delete_bot(db, bot_username=bot_username):
        return {"result":"Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed")

if __name__ == "__main__":
    #os.remove('clone_voice_source/New_Hero.mp3')
    uvicorn.run(app, host="localhost", port=8000)