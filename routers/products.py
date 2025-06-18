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

@router.put("/{product_id}")
def update_product(product_id: str, 
                  name: str = Query(None),
                  Tipo: str = Query(None),
                  Costo: float = Query(None),
                  precioVenta: float = Query(None),
                  stock: int = Query(None)):
    from db.models import Product
    with Session(engine) as session:
        product = session.exec(select(Product).where(Product.id == product_id)).first()
        if not product:
            all_products = session.exec(select(Product)).all()
            ids = [str(p.id) for p in all_products]
            return {"error": f"Producto no encontrado. IDs existentes: {ids}"}
        # Actualización de campos
        if name is not None:
            product.name = name
        if Tipo is not None:
            product.Tipo = Tipo
        if Costo is not None:
            product.Costo = float(Costo)
        if precioVenta is not None:
            product.precioVenta = float(precioVenta)
        if stock is not None:
            product.stock = int(stock)
        session.add(product)
        session.commit()
        session.refresh(product)
        return {
            "id": product.id,
            "name": product.name,
            "Tipo": product.Tipo,
            "Costo": product.Costo,
            "precioVenta": product.precioVenta,
            "stock": product.stock
        }

@router.delete("/{product_id}")
def delete_product(product_id: str):
    from db.models import Product
    with Session(engine) as session:
        product = session.exec(select(Product).where(Product.id == product_id)).first()
        if not product:
            return {"error": "Producto no encontrado"}
        session.delete(product)
        session.commit()
        return {"message": f"Producto {product_id} eliminado correctamente"}

