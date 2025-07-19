import uuid
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from db.models import Business, User, BlacklistUser
from db.connection import engine
from routers.auth import get_token_auth_header
from utils.email.email_utils import send_welcome_email

def handle_register_session(payload: dict = Depends(get_token_auth_header)):
    namespace = "https://emprendeplus.com/"
    user_id = payload.get("sub")
    name = payload.get(namespace + "name", "")
    email = payload.get(namespace + "email", "")

    if not user_id:
        return {"error": "No se pudo obtener el user_id desde el token"}

    with Session(engine) as session:
        blacklist_entry = session.exec(
            select(BlacklistUser).where(BlacklistUser.user_id == user_id)
        ).first()
        if blacklist_entry:
            raise HTTPException(status_code=403, detail="Usuario en blacklist")

        existing_user = session.exec(select(User).where(User.id == user_id)).first()
        if existing_user:
            if not existing_user.business:
                business = Business(
                    id=uuid.uuid4(),
                    name="Mi negocio",
                    description="",
                    owner_id=user_id
                )
                session.add(business)
                session.commit()
                session.refresh(business)

            return {
                "message": "Sesión ya registrada",
                "user_id": user_id,
            }

        user = User(id=user_id, name=name or "", business_name=None)
        session.add(user)
        session.commit()
        session.refresh(user)
        
        if email:
            send_welcome_email(to_email=email, name=name)

        business = Business(
            id=uuid.uuid4(),
            name="Mi negocio",
            description="",
            owner_id=user_id
        )
        session.add(business)
        session.commit()
        session.refresh(business)

        return {
            "message": "Usuario creado y sesión registrada",
            "user_id": user_id,
            "email": email,
            "name": name,
        }
