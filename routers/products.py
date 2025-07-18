from typing import Optional
from fastapi import APIRouter, Body, Depends, Query, HTTPException, UploadFile, File, Form, Request
from sqlmodel import Session, select
from db.connection import engine
from db.models import  Product, Business, User
from models import ProductCreate, ProductCreateFromUser, ProductRead, ProductUpdateInput
from routers.auth import get_current_user


router = APIRouter()

@router.get("/")
def get_products(user_id: str = Depends(get_current_user), request: Request = None):
    import os
    with Session(engine) as session:
        query = (
            select(Product)
            .join(Product.business)
            .where(Business.owner_id == user_id)
        )
        products = session.exec(query).all()
        result = []
        for product in products:
            image_url = None
            if product.image_path:
                filename = os.path.basename(product.image_path)
                if request:
                    base_url = str(request.base_url).rstrip("/")
                    image_url = f"{base_url}/image/{filename}"
                else:
                    image_url = f"/image/{filename}"
            product_dict = product.dict()
            product_dict["imageUrl"] = image_url
            result.append(product_dict)
        return result

@router.post("/")
async def create_product_for_user(
    data: ProductCreate = Body(...),
    user_id: str = Depends(get_current_user)
):
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()

        if not business:
            raise HTTPException(status_code=404, detail="Business not found for user")

        product = Product(
            sku=data.sku,
            type=data.type,
            cost=data.cost,
            name=data.name,
            sale_price=data.sale_price,
            stock=data.stock,
            business_id=business.id,
            description=data.description,
            discount=data.discount,
            min_stock_alert=data.min_stock_alert,
            supplier=data.supplier,
            status=data.status,
            color=data.color,
            width=data.width,
            height=data.height,
            depth=data.depth,
            weight=data.weight,
            tax_rate=data.tax_rate,
            created_at=data.created_at,
            updated_at=data.updated_at,
            rating=data.rating,
            image_path=None  # No imagen por JSON
        )

        session.add(product)
        session.commit()
        session.refresh(product)

        return product
    
@router.get("/{sku}")
def get_product_by_sku(sku: str, user_id: str = Depends(get_current_user), request: Request = None):
    import os
    with Session(engine) as session:
        product = session.exec(
            select(Product)
            .join(Product.business)
            .where(Product.sku == sku)
            .where(Business.owner_id == user_id)
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Si hay imagen, genera la URL absoluta para el frontend
        image_url = None
        if product.image_path:
            filename = os.path.basename(product.image_path)
            # Construye la URL absoluta usando el host del request
            if request:
                base_url = str(request.base_url).rstrip("/")
                image_url = f"{base_url}/image/{filename}"
            else:
                image_url = f"/image/{filename}"

        # Devuelve el producto como dict y agrega imageUrl
        product_dict = product.dict()
        product_dict["imageUrl"] = image_url

        return product_dict


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
    import os
    with Session(engine) as session:
        product = session.exec(select(Product).where(Product.sku == sku)).first()
        if not product:
            return {"error": f"Producto con SKU {sku} no encontrado"}
        # Elimina la imagen física si existe
        if product.image_path:
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), product.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        session.delete(product)
        session.commit()
        return {"message": f"Producto {sku} eliminado correctamente"}

@router.post("/upload-image/")
async def upload_product_image(
    sku: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    import os
    from fastapi.responses import JSONResponse

    # Verifica que el producto exista y pertenezca al usuario
    with Session(engine) as session:
        product = session.exec(
            select(Product)
            .join(Product.business)
            .where(Product.sku == sku)
            .where(Business.owner_id == user_id)
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not owned by user")

        # Crea la carpeta si no existe
        image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "image")
        os.makedirs(image_dir, exist_ok=True)

        # Guarda la imagen con un nombre único (por ejemplo, sku + extension original)
        ext = os.path.splitext(file.filename)[1]
        filename = f"{sku}{ext}"
        file_path = os.path.join(image_dir, filename)
        with open(file_path, "wb") as image_file:
            content = await file.read()
            image_file.write(content)

        # Guarda la ruta relativa en la base de datos
        product.image_path = f"image/{filename}"
        session.add(product)
        session.commit()
        session.refresh(product)

        return JSONResponse(content={"image_path": product.image_path})

