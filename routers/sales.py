from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.models import Business, Sale, SaleProduct, Product
from pydantic import BaseModel
from db.connection import engine
from models import SaleCreateInput, SaleProductInput, SaleRead, SaleUpdateInput
from routers.auth import get_current_user_id
from sqlalchemy.orm import selectinload

router = APIRouter()
    
@router.get("/", response_model=List[SaleRead])
def get_sales_for_user(user_id: str = Depends(get_current_user_id)):
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        sales = session.exec(
            select(Sale)
            .where(Sale.business_id == business.id)
            .options(
                selectinload(Sale.sale_products).selectinload(SaleProduct.product)  # carga SaleProduct.product
            )
        ).all()

        # Enriquecer los sale_products con los datos del producto
        for sale in sales:
            for sp in sale.sale_products:
                if sp.product:
                    sp.product_name = sp.product.name
                    sp.sale_price = sp.product.sale_price

        return sales


@router.post("/")
def create_sale_for_user(
    data: SaleCreateInput,
    user_id: str = Depends(get_current_user_id)
):
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        sale = Sale(
            business_id=business.id,
            sale_date=data.sale_date,
            total=sum(p.subtotal for p in data.products)
        )
        session.add(sale)
        session.flush()

        for p in data.products:
            sale_product = SaleProduct(
                sale_id=sale.id,
                product_id=p.product_id,
                quantity=p.quantity,
                subtotal=p.subtotal
            )
            session.add(sale_product)

            # ✅ Disminuir el stock del producto vendido
            product = session.get(Product, p.product_id)
            if product:
                if product.stock is not None:
                    if product.stock < p.quantity:
                        raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.sku}")
                    product.stock -= p.quantity
                    session.add(product)
        session.commit()
        session.refresh(sale)
        return {"message": "Venta creada", "sale_id": sale.id}

@router.get("/{sale_id}")
def get_sale_by_id(
    sale_id: UUID,
    user_id: str = Depends(get_current_user_id)
):
    with Session(engine) as session:
        # Validar que la venta sea del negocio del usuario
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()

        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        sale = session.exec(
            select(Sale).where(Sale.id == sale_id, Sale.business_id == business.id)
        ).first()

        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")

        # Obtener productos asociados a la venta
        sale_products = session.exec(
            select(SaleProduct).where(SaleProduct.sale_id == sale_id)
        ).all()

        products = []
        for sp in sale_products:
            product = session.get(Product, sp.product_id)
            if product:
                products.append({
    "sku": product.sku,
    "name": product.name,
    "quantity": sp.quantity,
    "price": product.sale_price,
    "discount": sp.discount,
    "subtotal": sp.subtotal
})

        return {
            "sale_id": str(sale.id),
            "sale_date": sale.sale_date,
            "total": sale.total,
            "products": products
        }

@router.put("/{sale_id}")
def update_sale_for_user(
    sale_id: UUID,
    data: SaleUpdateInput,
    user_id: str = Depends(get_current_user_id)
):
    with Session(engine) as session:
        # 1. Obtener el negocio del usuario
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        # 2. Obtener la venta
        sale = session.exec(
            select(Sale).where(Sale.id == sale_id, Sale.business_id == business.id)
        ).first()
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")

        # 3. Revertir el stock anterior
        prev_products = session.exec(
            select(SaleProduct).where(SaleProduct.sale_id == sale.id)
        ).all()
        for sp in prev_products:
            product = session.get(Product, sp.product_id)
            if product and product.stock is not None:
                product.stock += sp.quantity  # Devolver el stock anterior
                session.add(product)

        # 4. Eliminar sale_products antiguos
        for sp in prev_products:
            session.delete(sp)

        # 5. Crear nuevos sale_products y validar stock
        new_total = 0
        if data.products is not None:
            for p in data.products:
                product = session.get(Product, p.product_id)
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product {p.product_id} not found")

                if product.stock is not None and product.stock < p.quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for {p.product_id}")

                # Descontar nuevo stock
                product.stock -= p.quantity
                session.add(product)

                # Guardar relación sale-product
                sale_product = SaleProduct(
    sale_id=sale.id,
    product_id=p.product_id,
    quantity=p.quantity,
    subtotal=p.subtotal,
    discount=p.discount
)
                session.add(sale_product)
                new_total += p.subtotal

            sale.total = new_total

        # 6. Actualizar fecha si aplica
        if data.sale_date:
            sale.sale_date = data.sale_date

        session.add(sale)
        session.commit()
        session.refresh(sale)

        return {"message": "Venta actualizada", "sale_id": str(sale.id)}
    
    
@router.delete("/{sale_id}")
def delete_sale_for_user(
    sale_id: UUID,
    user_id: str = Depends(get_current_user_id)
):
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        sale = session.exec(
            select(Sale).where(Sale.id == sale_id, Sale.business_id == business.id)
        ).first()
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")

        session.delete(sale)
        session.commit()
        return {"message": "Venta eliminada"}
    

from sqlalchemy import extract
from collections import defaultdict

@router.get("/summary/monthly-summary")
def get_monthly_summary(user_id: str = Depends(get_current_user_id)):
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        # Traer todas las ventas del último año
        one_year_ago = datetime.today().replace(year=datetime.today().year - 1)

        sales = session.exec(
            select(Sale.sale_date, Sale.total)
            .where(Sale.business_id == business.id)
            .where(Sale.sale_date >= one_year_ago)
        ).all()

        # Agrupar por año y mes
        monthly_totals = defaultdict(float)
        for sale_date, total in sales:
            key = (sale_date.year, sale_date.month)
            monthly_totals[key] += total

        # Convertir a [{ date, value }]
        summary = [
            {
                "date": datetime(year, month, 1).isoformat(),
                "value": round(monthly_totals[(year, month)], 2),
            }
            for (year, month) in sorted(monthly_totals)
        ]

        return summary
