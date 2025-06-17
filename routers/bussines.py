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

@router.post("/create-business/")
def create_business(user_id: str = Query(...), name: str = Query(...), description: str = Query("")):
    """
    Crea un negocio asociado a un usuario existente. El id será UUID válido.
    """
    from db.models import Business
    import uuid
    with Session(engine) as session:
        # Verifica que el usuario exista
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            return {"error": "Usuario no encontrado"}
        business = Business(
            name=name,
            description=description,
            owner_id=user_id
        )
        session.add(business)
        session.commit()
        session.refresh(business)
        return {
            "id": str(business.id),
            "name": business.name,
            "description": business.description,
            "owner_id": business.owner_id
        }

@router.put("/update-business/{business_id}")
def update_business(business_id: str, name: str = Query(None), description: str = Query(None)):
    from db.models import Business
    import uuid
    try:
        business_uuid = uuid.UUID(business_id)
    except Exception:
        return {"error": "business_id debe ser un UUID válido"}
    with Session(engine) as session:
        business = session.exec(select(Business).where(Business.id == business_uuid)).first()
        if not business:
            return {"error": "Negocio no encontrado"}
        if name is not None:
            business.name = name
        if description is not None:
            business.description = description
        session.add(business)
        session.commit()
        session.refresh(business)
        return {
            "id": str(business.id),
            "name": business.name,
            "description": business.description,
            "owner_id": business.owner_id
        }
