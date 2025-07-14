from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, Session as SQLSession
from db.models import Business, Budget, Finance, Product, Sale, SaleProduct
from db.connection import engine,get_session
import csv, zipfile, io
from typing import List

router = APIRouter()

TABLE_MAP = {
    "business.csv": (Business, "business_id"),
    "budgets.csv": (Budget, "business_id"),
    "finances.csv": (Finance, "business_id"),
    "products.csv": (Product, "business_id"),
    "sales.csv": (Sale, "business_id"),
    "sale_products.csv": (SaleProduct, "sale_id")  
}

def parse_csv(content: str, model) -> List[SQLModel]:
    reader = csv.DictReader(io.StringIO(content))
    return [model(**row) for row in reader]

@router.post("/business/import")
def import_business_data(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Debe subir un archivo .zip")

    zip_bytes = file.file.read()
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
            files_in_zip = zip_file.namelist()
            required = list(TABLE_MAP.keys())

            if not any(f in files_in_zip for f in required):
                raise HTTPException(status_code=400, detail="Faltan archivos necesarios en el ZIP")

            load_order = [
                "business.csv",
                "budgets.csv",
                "finances.csv",
                "products.csv",
                "sales.csv",
                "sale_products.csv"
            ]

            for file_name in load_order:
                if file_name not in files_in_zip:
                    continue

                model, key_field = TABLE_MAP[file_name]
                csv_bytes = zip_file.read(file_name).decode("utf-8")
                items = parse_csv(csv_bytes, model)

                for item in items:
                    session.add(item)

            session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error al importar datos: {str(e)}")

    return {"detail": "Importación exitosa"}