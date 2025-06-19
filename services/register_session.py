# services/register_session.py

from fastapi import Depends
from sqlmodel import Session, select
from db.models import User
from db.connection import engine
from routers.auth import get_token_auth_header

def handle_register_session(payload: dict = Depends(get_token_auth_header)):
    # 📌 Namespace usado en tu Action de Auth0
    namespace = "https://emprendeplus.com/"
    user_id = payload.get("sub")
    name = payload.get(namespace + "name", "")
    email = payload.get(namespace + "email", "")

    if not user_id:
        return {"error": "No se pudo obtener el user_id desde el token"}

    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.id == user_id)).first()

        if existing_user:
            return {
                "message": "Sesión ya registrada",
                "user_id": user_id,
            }

        user = User(id=user_id, name=name or "", business_name=None)
        session.add(user)
        session.commit()
        session.refresh(user)

        return {
            "message": "Usuario creado y sesión registrada",
            "user_id": user_id,
            "email": email,
            "name": name,
        }
