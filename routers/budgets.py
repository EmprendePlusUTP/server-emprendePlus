# backend/app/routers/budgets.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from db.connection import engine
from db.models import Business, Budget
from models import BudgetCreate, BudgetRead
from routers.auth import get_current_user_id

router = APIRouter()

@router.get("/", response_model=List[BudgetRead])
def read_budgets(user_id: str = Depends(get_current_user_id)):
    """
    Lista el presupuesto definido para el negocio del usuario.
    """
    with Session(engine) as session:
        biz = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not biz:
            raise HTTPException(status_code=404, detail="Business not found")
        return session.exec(
            select(Budget).where(Budget.business_id == biz.id)
        ).all()

@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(
    data: BudgetCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Crea o actualiza una entrada de presupuesto (por categoría/subcategoría).
    """
    with Session(engine) as session:
        biz = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not biz:
            raise HTTPException(status_code=404, detail="Business not found")

        # Si ya existe presupuesto para esa cat/subcat, lo actualizamos
        existing = session.exec(
            select(Budget)
            .where(Budget.business_id == biz.id)
            .where(Budget.category == data.category)
            .where(Budget.subcategory == data.subcategory)
        ).first()

        if existing:
            existing.amount = data.amount
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        # Sino, lo creamos
        b = Budget(
            business_id=biz.id,
            category=data.category,
            subcategory=data.subcategory,
            amount=data.amount,
        )
        session.add(b)
        session.commit()
        session.refresh(b)
        return b
