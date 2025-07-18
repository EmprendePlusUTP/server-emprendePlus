from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.connection import engine
from db.models import Business, Sale, SaleProduct, Product, Finance, Budget
from routers.auth import get_current_user
from datetime import datetime
from collections import defaultdict, Counter
import openai
import os
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Falta OPENAI_API_KEY en el entorno")

class AdvisorRequest(BaseModel):
    message: str
    history: list[dict] = []
    
class AdvisorResponse(BaseModel):
    reply: str
    

@router.post("/", response_model=AdvisorResponse)
def advisor(
    req: AdvisorRequest,
    user = Depends(get_current_user),
):
    
    try:
        with Session(engine) as session:
            # Obtener negocio del usuario
            business = session.exec(
                select(Business).where(Business.owner_id == user["id"])
            ).first()
            if not business:
                raise HTTPException(status_code=404, detail="Business not found")

            # --- Ventas históricas ---
            one_year_ago = datetime.today().replace(year=datetime.today().year - 1)
            sales = session.exec(
                select(Sale)
                .where(Sale.business_id == business.id, Sale.sale_date >= one_year_ago)
            ).all()

            monthly_sales = defaultdict(float)
            for sale in sales:
                key = sale.sale_date.strftime("%Y-%m")
                monthly_sales[key] += sale.total

            # --- Productos vendidos ---
            product_counter = Counter()
            sale_products = session.exec(
                select(SaleProduct)
                .join(Sale)
                .where(Sale.business_id == business.id)
            ).all()
            for sp in sale_products:
                product_counter[sp.product_id] += sp.quantity

            # --- Producto estrella ---
            top_product = "No definido"
            if product_counter:
                top_sku = product_counter.most_common(1)[0][0]
                product = session.get(Product, top_sku)
                if product:
                    top_product = product.name

            # --- Lista de productos ---
            products = session.exec(
                select(Product)
                .join(Product.business)
                .where(Business.owner_id == user["id"])
            ).all()

            product_list = []
            for p in products:
                product_list.append({
                    "sku": p.sku,
                    "name": p.name,
                    "monthly_sales": product_counter.get(p.sku, 0),
                    "supplier": p.supplier,
                    "stock": p.stock
                })

            # --- Finanzas ---
            finances = session.exec(
                select(Finance).where(Finance.business_id == business.id)
            ).all()

            finance_summary = []
            for f in finances:
                finance_summary.append({
                    "date": f.date.strftime("%Y-%m-%d"),
                    "type": f.type,
                    "category": f.category,
                    "subcategory": f.subcategory,
                    "amount": f.amount
                })

            # --- Presupuestos ---
            budgets = session.exec(
                select(Budget).where(Budget.business_id == business.id)
            ).all()

            budget_summary = []
            for b in budgets:
                budget_summary.append({
                    "category": b.category,
                    "subcategory": b.subcategory,
                    "amount": b.amount
                })

            # --- Prompt completo ---
            system_prompt = (
                "Eres el Asistente Inteligente de EmprendePlus.\n"
                "Tu función es asesorar a emprendedores en temas de ventas, inventario, producto estrella, finanzas y presupuestos.\n\n"

                "**Antes de responder:** analiza el mensaje del usuario y decide internamente si se refiere a alguno de estos temas:\n"
                "- ventas\n"
                "- inventario\n"
                "- producto estrella\n"
                "- finanzas (ingresos, egresos, control financiero)\n"
                "- presupuestos\n"
                "- preguntas generales\n\n"

                "**Usa solo el contexto relevante** para evitar sobrecargar la respuesta. No menciones esta clasificación en tu mensaje.\n"
                "Si la conversación tiene mensajes anteriores, toma en cuenta su contenido para dar continuidad.\n\n"

                "**Reglas para tu respuesta:**\n"
                "- Siempre responde en **español**, con un tono profesional y cercano.\n"
                "- **Evita repetir datos innecesarios** si no aportan valor.\n"
                "- Sé claro, directo y estructurado.\n\n"

                "**Formato sugerido de respuesta:**\n"
                "1. **Resumen** breve de la situación actual\n"
                "2. **Puntos de mejora** numerados\n"
                "3. **Acciones recomendadas** con prioridad (pueden incluir ideas, alertas o estrategias)\n"
                "4. Si necesitas más datos, **haz preguntas concretas** al usuario\n\n"

                "**Contexto disponible:**\n"
                f"- Nombre del negocio: {business.name}\n"
                f"- Moneda: {business.currency}\n"
                f"- Historial de ventas mensuales: {dict(monthly_sales)}\n"
                f"- Producto estrella: {top_product}\n"
                f"- Lista de productos (ventas, proveedor, stock): {product_list}\n"
                f"- Finanzas (ingresos y egresos): {finance_summary}\n"
                f"- Presupuestos por categoría: {budget_summary}\n"
            )

            messages = [{"role": "system", "content": system_prompt}] + req.history + [{"role": "user", "content": req.message}]

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
            )

            reply = response.choices[0].message.content
            return {"reply": reply}

    except Exception as e:
        logger.exception("Error en /advisor")
        raise HTTPException(status_code=500, detail="Error interno del asesor.")
