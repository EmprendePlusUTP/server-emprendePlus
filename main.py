from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.utils import create_tables
from contextlib import asynccontextmanager
from db import models
from routers import users, products, sales
from routers.advisor import router as advisor_router

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

# Routers
app.include_router(users.router, prefix="/users", tags=["Usuarios"])
app.include_router(products.router, prefix="/products", tags=["Productos"])
app.include_router(sales.router, prefix="/sales", tags=["Ventas"])
app.include_router(advisor_router) 

# Ruta base
@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a Emprende+"}
