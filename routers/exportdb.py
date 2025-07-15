from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import SQLModel, Session as SQLSession, create_engine
from sqlalchemy.orm import Session
from db.models import Business, Budget, Finance, Product, Sale, SaleProduct
from io import BytesIO
import tempfile, shutil, os
from typing import List

router = APIRouter()

# Conexion local 
DATABASE_URL = "sqlite:///./database.db"  # O tu URL real
main_engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(main_engine) as session:
        yield session

@router.get("/business/export-db")
def export_business_db(business_id: str, session: Session = Depends(get_session)):
    # Crear una base de datos SQLite temporal
    with tempfile.TemporaryDirectory() as tmpdirname:
        db_path = os.path.join(tmpdirname, "database.db")
        engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(engine)

        with SQLSession(engine) as tmp_session:
            # Copiar Business
            business = session.query(Business).filter(Business.id == business_id).first()
            if business:
                tmp_session.add(Business.from_orm(business))

            # Copiar Finance
            finances = session.query(Finance).filter(Finance.business_id == business_id).all()
            tmp_session.add_all([Finance.from_orm(f) for f in finances])

            # Copiar Budget
            budgets = session.query(Budget).filter(Budget.business_id == business_id).all()
            tmp_session.add_all([Budget.from_orm(b) for b in budgets])

            # Copiar Product
            products = session.query(Product).filter(Product.business_id == business_id).all()
            tmp_session.add_all([Product.from_orm(p) for p in products])

            # Copiar Sale
            sales = session.query(Sale).filter(Sale.business_id == business_id).all()
            tmp_session.add_all([Sale.from_orm(s) for s in sales])

            # Copiar SaleProduct
            sale_ids = [s.id for s in sales]
            sale_products = session.query(SaleProduct).filter(SaleProduct.sale_id.in_(sale_ids)).all()
            tmp_session.add_all([SaleProduct.from_orm(sp) for sp in sale_products])

            tmp_session.commit()

        # Leer el archivo .db y devolverlo como streaming
        buffer = BytesIO()
        with open(db_path, "rb") as f:
            shutil.copyfileobj(f, buffer)
        buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/x-sqlite3", headers={
        "Content-Disposition": f"attachment; filename=business_{business_id}.db"
    })
