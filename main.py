from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.utils import create_tables
from contextlib import asynccontextmanager
from db import models  # Asegúrate de que este módulo exista y contenga los modelos
from routers import business, users, products, sales
from services.register_session import handle_register_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()  # Crea las tablas al iniciar la aplicación
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos los routers
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(products.router, prefix="/api/products", tags=["Productos"])
app.include_router(sales.router, prefix="/sales", tags=["Ventas"])
app.include_router(business.router, prefix="/api/business", tags=["Negocios"])

# Ruta base
@app.get("/")
def read_root():
    return {"Base de datos creada"}

@app.post("/api/register-session")
def register_session(response=Depends(handle_register_session)):
    return response