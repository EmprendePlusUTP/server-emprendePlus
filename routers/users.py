from fastapi import APIRouter
from db.models import User
from db.connection import engine
from sqlmodel import Session, select

router = APIRouter()

@router.get("/")
def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users

@router.post("/")
def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
