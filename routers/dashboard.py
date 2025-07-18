# backend/app/routers/dashboard.py

from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime, timedelta, timezone
from db.connection import engine
from db.models import Business, Sale, SaleProduct, Product
from routers.auth import get_current_user

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(user_id: str = Depends(get_current_user)):
    """
    Devuelve resumen para el dashboard: ingresos, órdenes, conversión, producto estrella.
    """
    with Session(engine) as session:
        # 1. Obtener negocio asociado al usuario
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        today = datetime.today()
        year, month = today.year, today.month
        first_day = datetime(year, month, 1)
        last_month_day = first_day - timedelta(days=1)

        # 2. Filtrar ventas de este mes
        sales_this_month = session.exec(
            select(Sale)
            .where(Sale.business_id == business.id)
            .where(Sale.sale_date >= first_day)
        ).all()

        total_revenue = sum(s.total for s in sales_this_month)
        total_orders = len(sales_this_month)

        # 3. Producto más vendido (por cantidad en este mes)
        top_product = session.exec(
            select(
                SaleProduct.product_id,
                func.sum(SaleProduct.quantity).label("qty"),
                func.sum(SaleProduct.subtotal).label("revenue")
            )
            .join(Sale)
            .where(Sale.business_id == business.id)
            .where(Sale.sale_date >= first_day)
            .group_by(SaleProduct.product_id)
            .order_by(func.sum(SaleProduct.quantity).desc())
            .limit(1)
        ).first()

        top_product_info = None
        growth_rate = 0.0
        growth_change = 0.0
        revenue_change = 0.0
        if top_product:
            sku, total_sold, revenue = top_product

            product = session.get(Product, sku)

            # 4. Comparación con mes anterior
            previous_month_start = datetime(last_month_day.year, last_month_day.month, 1)
            previous_month_end = first_day

            # Mes anterior al anterior (para growth_change)
            two_months_ago_end = previous_month_start
            two_months_ago_start = two_months_ago_end - timedelta(days=1)
            two_months_ago_start = datetime(two_months_ago_start.year, two_months_ago_start.month, 1)

            # Revenues de meses anteriores
            previous_month_revenue = session.exec(
                select(func.sum(Sale.total))
                .where(Sale.business_id == business.id)
                .where(Sale.sale_date >= previous_month_start)
                .where(Sale.sale_date < previous_month_end)
            ).first() or 0

            two_months_ago_revenue = session.exec(
                select(func.sum(Sale.total))
                .where(Sale.business_id == business.id)
                .where(Sale.sale_date >= two_months_ago_start)
                .where(Sale.sale_date < two_months_ago_end)
            ).first() or 0

            # Variaciones
            if previous_month_revenue == 0:
                revenue_change = 100.0 if total_revenue > 0 else 0.0
            else:
                revenue_change = round(((total_revenue - previous_month_revenue) / previous_month_revenue) * 100, 1)

            if previous_month_revenue == 0:
                growth_rate = round(total_revenue * 100, 1) if total_revenue > 0 else 0.0
            else:
                growth_rate = round(((total_revenue - previous_month_revenue) / previous_month_revenue) * 100, 1)

            if two_months_ago_revenue == 0:
             previous_growth_rate = round(previous_month_revenue * 100, 1) if previous_month_revenue > 0 else 0.0
            else:
                previous_growth_rate = round(((previous_month_revenue - two_months_ago_revenue) / two_months_ago_revenue) * 100, 1)

            growth_change = round(growth_rate - previous_growth_rate, 1)
        return {
    "total_revenue": total_revenue,
    "total_orders": total_orders,
    "growth_rate": growth_rate,
    "growth_change": growth_change,
    "revenue_change": revenue_change,
    "top_product": top_product_info,
}

@router.get("/wordcloud")
def get_wordcloud_data(user_id: str = Depends(get_current_user)):
    """
    Devuelve una lista de productos más vendidos en formato { text, value }
    útil para la nube de palabras.
    """
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        result = session.exec(
            select(
                SaleProduct.product_id,
                func.sum(SaleProduct.quantity).label("total_qty")
            )
            .join(Sale)
            .where(Sale.business_id == business.id)
            .group_by(SaleProduct.product_id)
            .order_by(func.sum(SaleProduct.quantity).desc())
        ).all()

        # Convertimos a formato esperado para WordCloud
        wordcloud_data = []
        for sku, qty in result:
            product = session.get(Product, sku)
            wordcloud_data.append({
                "text": product.name if product else sku,
                "value": qty
            })

        return wordcloud_data

@router.get("/sales-activity")
def get_sales_activity(user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        sales = session.exec(
            select(Sale).where(Sale.business_id == business.id)
        ).all()

        # Agrupar ventas por fecha (día)
        sales_by_day: defaultdict[str, list[Sale]] = defaultdict(list)

        for sale in sales:
            sale_dt = sale.sale_date
            if sale_dt.tzinfo is None or sale_dt.tzinfo.utcoffset(sale_dt) != timedelta(hours=-5):
                sale_dt = sale_dt.astimezone(timezone(timedelta(hours=-5)))

            sale_day_str = sale_dt.date().isoformat()
            sales_by_day[sale_day_str].append(sale_dt)

        total_days = len(sales_by_day)
        heatmap = [[0 for _ in range(24)] for _ in range(7)]

        # Acumular conteos por hora/día
        for sale_day_sales in sales_by_day.values():
            for dt in sale_day_sales:
                day = (dt.weekday() + 1) % 7
                hour = dt.hour
                heatmap[day][hour] += 1

        # Promediar dividiendo por número de días únicos
        if total_days > 0:
            for day in range(7):
                for hour in range(24):
                    heatmap[day][hour] = round(heatmap[day][hour] / total_days, 2)

        # Formato para ECharts
        data = [[hour, day, heatmap[day][hour]] for day in range(7) for hour in range(24)]

        return {"data": data}
    
@router.get("/star-product-comparison")
def get_top_product_comparison(user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        # Buscar negocio
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        # 1. Encontrar el producto más vendido (producto estrella)
        top_product_result = session.exec(
            select(
                SaleProduct.product_id,
                func.sum(SaleProduct.quantity).label("qty")
            )
            .join(Sale)
            .where(Sale.business_id == business.id)
            .group_by(SaleProduct.product_id)
            .order_by(func.sum(SaleProduct.quantity).desc())
            .limit(1)
        ).first()

        if not top_product_result:
            return []

        top_product_id, _ = top_product_result

        # 2. Obtener ventas de todos los productos
        sales_data = session.exec(
            select(Sale.sale_date, SaleProduct.product_id, SaleProduct.quantity)
            .join(SaleProduct, Sale.id == SaleProduct.sale_id)
            .where(Sale.business_id == business.id)
        ).all()

        # Inicializar contadores por mes
        star_product_sales = defaultdict(int)
        other_product_sales = defaultdict(list)

        for sale_date, product_id, quantity in sales_data:
            month_label = sale_date.strftime("%b")  # "Jan", "Feb", etc.
            if product_id == top_product_id:
                star_product_sales[month_label] += quantity
            else:
                other_product_sales[month_label].append(quantity)
        
        month_label = sale_date.strftime("%b")  # "Jan", "Feb", etc.
        spanish_months = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}
        # Generar lista de meses (Jan a Dec) en orden
        month_order = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        month_label = spanish_months[sale_date.month]
        result = []
        for month in month_order:
            primary = star_product_sales.get(month, 0)
            other_quantities = other_product_sales.get(month, [])
            secondary = round(sum(other_quantities) / len(other_quantities), 2) if other_quantities else 0
            result.append({
                "month": month,
                "primary": primary,
                "secondary": secondary
            })

        return result
    
@router.get("/star-product", response_model=dict)
def get_star_product_summary(user_id: str = Depends(get_current_user)):
    """
    Devuelve el nombre del producto estrella, su valor total anual y la comparación mensual.
    """
    with Session(engine) as session:
        business = session.exec(
            select(Business).where(Business.owner_id == user_id)
        ).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        # Encontrar el producto más vendido por cantidad total anual
        top_product_result = session.exec(
            select(
                SaleProduct.product_id,
                func.sum(SaleProduct.quantity).label("qty"),
                func.sum(SaleProduct.subtotal).label("total_value")
            )
            .join(Sale)
            .where(Sale.business_id == business.id)
            .group_by(SaleProduct.product_id)
            .order_by(func.sum(SaleProduct.quantity).desc())
            .limit(1)
        ).first()

        if not top_product_result:
            raise HTTPException(status_code=204, detail="No sales found")

        top_product_id, qty, total_value = top_product_result

        product = session.get(Product, top_product_id)
        if not product:
            raise HTTPException(status_code=204, detail="Product not found")

        # Traer data del endpoint comparativo
        comparison = get_top_product_comparison(user_id)

        return {
            "name": product.name,
            "product_qty": qty,
            "total_value": total_value,
            "monthly_comparison": comparison
        }