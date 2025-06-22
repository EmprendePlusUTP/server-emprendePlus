# backend/app/routers/finances.py
from datetime import date, datetime
from typing import List, Tuple
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlmodel import Session, func, select

from db.connection import engine
from db.models import Business, Finance, Sale
from models import FinanceCreate, FinanceRead
from routers.auth import get_current_user_id


router = APIRouter()


@router.get("/", response_model=List[FinanceRead])
def read_finances(user_id: str = Depends(get_current_user_id)):
    """
    Devuelve:
    - Un registro virtual tipo 'income' por cada fecha en la que hubo ventas,
      con category=subcategory="Ventas Diarias" y amount = suma de ventas de ese día.
    - Todas las transacciones manuales (income/expense).
    """
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(404, "Business not found")

        # 1) Agrupar ventas por fecha
        sales_per_day: List[Tuple[date, float]] = session.exec(
            select(
                Sale.sale_date,
                func.sum(Sale.total).label("daily_total")
            )
            .where(Sale.business_id == business.id)
            .group_by(Sale.sale_date)
            .order_by(Sale.sale_date.desc())
        ).all()

        # 2) Crear registros virtuales de tipo income para cada día
        virtuals = []
        for sale_date, daily_total in sales_per_day:
            virtuals.append(
                Finance(
                    id=uuid4().int & 0x7FFFFFFF,
                    business_id=business.id,
                    date=sale_date,
                    type="income",
                    category="Ventas Diarias",
                    subcategory="Ventas Diarias",
                    amount=float(daily_total),
                    description=f"Ventas del día {sale_date}"
                )
            )

        # 3) Obtener transacciones manuales
        manual_txs = session.exec(
            select(Finance)
            .where(Finance.business_id == business.id)
            .order_by(Finance.date.desc())
        ).all()

        # 4) Devolver primero las ventas diarias, luego tus Finance guardadas
        return virtuals + manual_txs


@router.post("/", response_model=FinanceRead, status_code=201)
def create_finance(
    data: FinanceCreate = Body(...),
    user_id: str = Depends(get_current_user_id),
):
    """
    Crea una transacción manual (income o expense).
    """
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(404, "Business not found")

        fin = Finance(
            business_id=business.id,
            date=data.date,
            type=data.type,
            category=data.category,
            subcategory=data.subcategory,
            amount=data.amount,
            description=data.description,
        )
        session.add(fin)
        session.commit()
        session.refresh(fin)
        return fin

@router.delete("/{finance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_finance(
    finance_id: int,
    user_id: str = Depends(get_current_user_id),
):
    """
    Elimina una transacción Finance por su ID, solo si pertenece al negocio del usuario.
    """
    with Session(engine) as session:
        # Validar negocio del usuario
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        # Encontrar la transacción
        fin = session.exec(
            select(Finance)
            .where(Finance.id == finance_id)
            .where(Finance.business_id == business.id)
        ).first()
        if not fin:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Eliminar y confirmar
        session.delete(fin)
        session.commit()

    # 204 No Content
    return