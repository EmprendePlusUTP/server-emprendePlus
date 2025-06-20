from typing import Optional
from fastapi import APIRouter, Body, Depends, Query, HTTPException
from sqlmodel import Session, select
from db.connection import engine
from db.models import  Product, Business, User
from models import ProductCreate, ProductCreateFromUser, ProductRead, ProductUpdateInput
from routers.auth import get_current_user_id


router = APIRouter()

@router.get("/")
def get_products(user_id: str = Depends(get_current_user_id)):
    with Session(engine) as session:
        # Filtra productos del negocio cuyo owner_id es el usuario actual
        query = (
            select(Product)
            .join(Product.business)
            .where(Business.owner_id == user_id)
        )
        products = session.exec(query).all()
        return products

@router.post("/")
def create_product_for_user(
    product_data: ProductCreate,
    user_id: str = Depends(get_current_user_id)
):
    with Session(engine) as session:
        # Obtener el negocio del usuario autenticado
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()

        if not business:
            raise HTTPException(status_code=404, detail="Business not found for user")

        product = Product(
            sku=product_data.sku,
            type=product_data.type,
            cost=product_data.cost,
            name=product_data.name,
            sale_price=product_data.sale_price,
            stock=product_data.stock,
            business_id=business.id 
        )

        session.add(product)
        session.commit()
        session.refresh(product)

        return product

@router.get("/{sku}", response_model=ProductRead)
def get_product_by_sku(sku: str, user_id: str = Depends(get_current_user_id)):
    with Session(engine) as session:
        product = session.exec(
            select(Product)
            .join(Product.business)
            .where(Product.sku == sku)
            .where(Business.owner_id == user_id)
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product

@router.patch("/{sku}")
def update_product(
    sku: str,
    data: ProductUpdateInput = Body(...),
):
    with Session(engine) as session:
        product = session.exec(select(Product).where(Product.sku == sku)).first()
        if not product:
            return {"error": f"Producto con SKU {sku} no encontrado"}

        for field, value in data.dict(exclude_unset=True).items():
            setattr(product, field, value)

        session.add(product)
        session.commit()
        session.refresh(product)

        return product

@router.delete("/{sku}")
def delete_product(sku: str):
    with Session(engine) as session:
        product = session.exec(select(Product).where(Product.sku == sku)).first()
        if not product:
            return {"error": f"Producto con SKU {sku} no encontrado"}
        session.delete(product)
        session.commit()
        return {"message": f"Producto {sku} eliminado correctamente"}

