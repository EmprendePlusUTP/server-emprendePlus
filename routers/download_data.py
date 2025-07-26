from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from db.connection import engine
from db.models import Finance, Product, Sale

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/business/finances")
def get_finances(session: Session = Depends(get_session)):
    finances = session.exec(select(Finance)).all()
    return [finance.dict() for finance in finances]

@router.get("/business/products")
def get_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return [product.dict() for product in products]

@router.get("/business/sales")
def get_sales(session: Session = Depends(get_session)):
    sales = session.exec(select(Sale)).all()
    return [sale.dict() for sale in sales]
