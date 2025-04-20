from sqlmodel import SQLModel
from .connection import engine

def create_tables():
    SQLModel.metadata.create_all(engine)
