from sqlmodel import Session, select
from db.models import User
from db.connection import engine

def create_user_db(user_id: str, user_name: str):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.id == user_id)).first()
        if existing:
            return existing
        user = User(id=user_id, name=user_name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_user_by_id(user_id: str):
    with Session(engine) as session:
        return session.exec(select(User).where(User.id == user_id)).first()
