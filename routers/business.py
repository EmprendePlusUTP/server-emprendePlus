from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from db.models import User, Business
from db.connection import engine
from sqlmodel import Session, select
from models import BusinessUpdate
from routers.auth import get_current_user, get_token_auth_header
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4

router = APIRouter()

@router.get("/business-settings", response_model=Business)
def get_business_settings(user = Depends(get_current_user)):
    """
    Obtiene la configuración del negocio asociado al usuario autenticado.
    """
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user["id"])
        ).first()

        if not business:
            raise HTTPException(status_code=404, detail="Negocio no encontrado")

        return business


@router.post("/create-business/")
def create_business(user_id: str = Query(...), name: str = Query(...), description: str = Query("")):
    """
    Crea un negocio asociado a un usuario existente. El id será UUID válido.
    """
    from db.models import Business
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        business = Business(
            id=uuid4(),
            name=name,
            description=description,
            owner_id=user_id
        )
        session.add(business)
        session.commit()
        session.refresh(business)

        return business


@router.patch("/update-business/")
def update_business_by_user(
    current_user = Depends(get_current_user),
    data: BusinessUpdate = Body(...)
):
    with Session(engine) as session:
        # Buscar usuario por su auth0_id
        user = session.exec(select(User).where(User.id == current_user["id"])).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no registrado")

        business = session.exec(select(Business).where(Business.owner_id == current_user["id"])).first()
        if not business:
            raise HTTPException(status_code=404, detail="Negocio no encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(business, key, value)

        session.add(business)
        session.commit()
        session.refresh(business)

        return business
