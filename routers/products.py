from fastapi import APIRouter
from sqlmodel import Session, select
from db.connection import engine
from db.models import Product

router = APIRouter()

@router.get("/")
def get_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return products

@router.post("/")
def create_product(product: Product):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
