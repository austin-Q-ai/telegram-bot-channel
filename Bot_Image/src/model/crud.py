from sqlalchemy.orm import Session, sessionmaker
from .models import User
from ..chat_box.chat import greate_chat


def create_user(db: Session, id:int):
    status, chat_id = greate_chat(id=id)
    if not status:
        return False
    db_user = User(id=id, chat_id=chat_id, response=None)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return True

def update_repsonse(db: Session, id:int, response:str):
    user = db.query(User).filter(User.id == id).update({"response" : response})
    db.commit()
    return user

def get_user_by_id(db: Session, id:int):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return False
    return user

def delete_user(db:sessionmaker, id:int):
    try:
        db.query(User).filter(User.id == id).delete()
        db.commit()
        return True
    except:
        return False