from fastapi import APIRouter
from sqlmodel import Session, select
from db.connection import engine
from db.models import Sale

router = APIRouter()

@router.get("/")
def get_sales():
    with Session(engine) as session:
        sales = session.exec(select(Sale)).all()
        return sales

@router.post("/")
def create_sale(sale: Sale):
    with Session(engine) as session:
        session.add(sale)
        session.commit()
        session.refresh(sale)
        return sale
