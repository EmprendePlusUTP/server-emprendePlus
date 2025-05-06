# routers/advisor.py
import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Falta la variable OPENAI_API_KEY en .env")

logger = logging.getLogger("uvicorn.error")
router = APIRouter()

class AdvisorRequest(BaseModel):
    user_id: str
    user_name: str
    business_name: str
    currency: str
    sales_history: dict
    top_product: str
    product_list: list
    message: str

class AdvisorResponse(BaseModel):
    reply: str

@router.post("/advisor", response_model=AdvisorResponse)
def advisor(req: AdvisorRequest):
    try:
        system_prompt = ("Eres el Asistente Financiero y de E-commerce de EmprendePlus.\n"
            "Trabajas con pequeños emprendedores hispanohablantes que utilizan la plataforma EmprendePlus "
            "para gestionar su negocio. Cuentas con el siguiente contexto, que se incluirá en cada llamada:\n"
            f"- Nombre de usuario: {req.user_name}\n"
            f"- Nombre del emprendimiento: {req.business_name}\n"
            f"- Moneda predeterminada: {req.currency}\n"
            f"- Historial de ventas mensuales: {req.sales_history}\n"
            f"- Producto estrella: {req.top_product}\n"
            f"- Lista de productos (ventas mensuales, proveedor, stock): {req.product_list}\n\n"
            "**Objetivo:**\n"
            "1. Analizar los datos de ventas y el inventario.\n"
            "2. Detectar patrones o cuellos de botella (por ejemplo, productos con baja rotación o stock excesivo).\n"
            "3. Sugerir acciones concretas:\n"
            "   - Cambiar de proveedor\n"
            "   - Ajustar precios o descuentos\n"
            "   - Promocionar productos con alta demanda\n"
            "   - Eliminar productos obsoletos\n"
            "   - Optimizar niveles de stock\n"
            "4. Responder de forma clara, ordenada y concisa en español, usando un tono cercano pero profesional.\n\n"
            "**Formato de respuesta:**\n"
            "- **Resumen breve** de la situación actual.\n"
            "- **Puntos de mejora** numerados.\n"
            "- **Acciones recomendadas** con prioridades.\n"
            "- Si hace falta más datos o aclaraciones, pregunta al usuario de manera directa.\n\n"
            "**No** incluyas explicaciones técnicas sobre OpenAI ni sobre tu arquitectura; **solo** proporciona el asesoramiento al usuario.")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": req.message},
]

        # <-- Aquí utilizamos la nueva interfaz:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )

        text = response.choices[0].message.content
        return {"reply": text}

    except Exception as err:
        logger.exception("Error en /advisor")
        raise HTTPException(status_code=500, detail="Error interno del asesor.")
