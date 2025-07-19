from fastapi import Depends, FastAPI
from routers import blacklist  # Asegúrate de tenerlo disponible
from fastapi.middleware.cors import CORSMiddleware
from db.utils import create_tables
from contextlib import asynccontextmanager
from db import models  # Asegúrate de que este módulo exista y contenga los modelos
from routers import budgets, business, dashboard, finances, users, products, sales, advisor, generate_dummy_data
from routers.generate_dummy_data import router as dummy_router


from services.register_session import handle_register_session
from fastapi.staticfiles import StaticFiles
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "image")
app.mount("/image", StaticFiles(directory=IMAGE_DIR), name="image")

app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(products.router, prefix="/api/products", tags=["Productos"])
app.include_router(sales.router, prefix="/api/sales", tags=["Ventas"])
app.include_router(business.router, prefix="/api/business", tags=["Negocios"])
app.include_router(finances.router, prefix="/api/finances", tags=["Finanzas"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Presupuestos"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Tablero"])
app.include_router(advisor.router, prefix="/api/advisor", tags=["Modaldobot"])
app.include_router(generate_dummy_data.router, prefix="/api/generate-dummy-data", tags=["Generar Data"])
app.include_router(blacklist.router, tags=["Blacklist"])


# Ruta base
@app.get("/")
def read_root():
    return {"Base de datos creada"}

@app.post("/api/register-session")
def register_session(response=Depends(handle_register_session)):
    return response