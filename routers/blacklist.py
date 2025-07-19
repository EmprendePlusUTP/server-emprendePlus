from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from db.models import BlacklistUser
from db.connection import engine
from pydantic import BaseModel
from fastapi import HTTPException
router = APIRouter()

class BlacklistRequest(BaseModel):
    user_id: str
    reason: str = ""

@router.post("/api/blacklist-user")
def blacklist_user(request: BlacklistRequest):
    user_id = request.user_id
    reason = request.reason
    with Session(engine) as session:
        exists = session.exec(select(BlacklistUser).where(BlacklistUser.user_id == user_id)).first()
        if exists:
            raise HTTPException(status_code=409, detail="Usuario ya en blacklist")
        entry = BlacklistUser(user_id=user_id, reason=reason)
        session.add(entry)
        session.commit()
        return {"msg": "Usuario añadido a blacklist"}
    
@router.delete("/api/blacklist-user/{user_id}")
def remove_from_blacklist(user_id: str):
    with Session(engine) as session:
        entry = session.exec(select(BlacklistUser).where(BlacklistUser.user_id == user_id)).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Usuario no está en blacklist")
        session.delete(entry)
        session.commit()
        return {"msg": f"Usuario {user_id} eliminado de blacklist"}