'''
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from db.connection import engine
from db.models import Product
from auth import verify_jw
from fastapi import HTTPException

router = APIRouter()

@router.get("/products")
def get_products(user_id: str = Query(None)):

    # if user_id and user_id != user_auth_id:
    #     raise HTTPException(status_code=403, detail="No autorizado para ver estos productos")

    with Session(engine) as session:
        query = select(Product)

        if user_id:
            query = query.where(Product.business.has(owner_id=user_id))

        products = session.exec(query).all()
        return products

#TODO: Conectar base de datos con endpoint ^ y al llamar al endpoint se deben obtener todos los productos. Este call debe tener un filtro (id del usuario o emprendimiento con Auth0) 

@router.post("/")
def create_product(product: Product):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product



'''
from fastapi import APIRouter, Query, HTTPException
from sqlmodel import Session, select
from db.connection import engine
from db.models import Product, Business, User

router = APIRouter()

@router.get("/")
def get_products(user_id: str = Query(None), business_id: str = Query(None)):
    with Session(engine) as session:
        query = select(Product)
        if user_id:
            # Filtra productos cuyos negocios asociados tengan owner_id igual a user_id.
            query = query.join(Product.business).where(Business.owner_id == user_id)
        elif business_id:
            # Filtra productos asociados al negocio cuyo id coincida.
            query = query.join(Product.business).where(Business.id == business_id)
        products = session.exec(query).all()
        return products

@router.post("/")
def create_product(product: Product):
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    
