from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from db.models import User, Business
from db.connection import engine
from sqlmodel import Session, select
from routers.auth import get_token_auth_header
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from uuid import UUID

router = APIRouter()

class BusinessOut(BaseModel):
    id: UUID
    name: str
    description: str
    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: str
    name: str
    business_name: Optional[str]
    businesses: List[BusinessOut] = []
    class Config:
        orm_mode = True


@router.post("/")
def create_user_query(
    user_id: str = Query(...),
    user_name: str = Query(...),
    business_name: str = Query(None)
):
    import uuid
    from db.models import Business
    if not user_id or not user_name:
        return {"error": "user_id y user_name son obligatorios"}
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.id == user_id)).first()
        if existing:
            return existing
        user = User(id=user_id, name=user_name, business_name=business_name)
        session.add(user)
        session.commit()
        session.refresh(user)
        # Si se proporciona business_name, crear un negocio automáticamente
        if business_name:
            business = Business(
                id=uuid.uuid4(),
                name=business_name,
                description="",
                owner_id=user_id
            )
            session.add(business)
            session.commit()
            session.refresh(business)
        return user

@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: str):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id).options(selectinload(User.businesses))
        user = session.exec(statement).first()
        if not user:
            return {"error": "Usuario no encontrado"}
        return user

@router.put("/{user_id}")
def update_user(user_id: str, user_name: str = Query(None), business_name: str = Query(None)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            return {"error": "Usuario no encontrado"}
        if user_name is not None:
            user.name = user_name
        if business_name is not None:
            user.business_name = business_name
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@router.delete("/{user_id}")
def delete_user(user_id: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            return {"error": "Usuario no encontrado"}
        session.delete(user)
        session.commit()
        return {"message": "Usuario eliminado"}

