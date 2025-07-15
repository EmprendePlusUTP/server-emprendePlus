from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session as MainSession
from sqlmodel import SQLModel, Session as TempSession
from sqlalchemy import create_engine
from db.models import Business, Budget, Finance, Product, Sale, SaleProduct
import shutil, tempfile, os
from typing import Type

router = APIRouter()


DATABASE_URL = "sqlite:///./database.db"
main_engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with MainSession(bind=main_engine) as session:
        yield session
        
TABLES: list[Type[SQLModel]] = [Business, Budget, Finance, Product, Sale, SaleProduct]

@router.post("/business/import-db")
def import_business_from_db(
    file: UploadFile = File(...),
    session: MainSession = Depends(get_session)
):
    if not file.filename.endswith(".db"):
        raise HTTPException(status_code=400, detail="Debe subir un archivo .db")

    try:
        # Guardar archivo .db temporalmente
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "imported.db")
            with open(db_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            # Crear motor y sesión para base temporal
            temp_engine = create_engine(f"sqlite:///{db_path}")
            with TempSession(temp_engine) as temp_session:
                # Obtener business principal
                business: Business = temp_session.query(Business).first()
                if not business:
                    raise HTTPException(status_code=400, detail="No se encontró ningún negocio en el archivo.")
                business_id = business.id

                # Verificar si el negocio ya existe en la base principal
                if not session.get(Business, business_id):
                    session.add(Business.from_orm(business))

                # Registrar IDs existentes para evitar duplicados
                existing_ids = {
                    model.__name__: {r.id for r in session.query(model).all()}
                    for model in TABLES if hasattr(model, "id")
                }

                # Recorrer tablas restantes
                for model in TABLES:
                    if model == Business:
                        continue
                    temp_records = temp_session.query(model).all()

                    for record in temp_records:
                        if hasattr(record, "business_id") and record.business_id != business_id:
                            continue  
                        if model.__name__ in existing_ids and getattr(record, "id", None) in existing_ids[model.__name__]:
                            continue  

                        # Validar claves foráneas (sale_id en SaleProduct)
                        if isinstance(record, SaleProduct):
                            if not session.get(Sale, record.sale_id):
                                continue

                        session.add(model.from_orm(record))

                session.commit()

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al importar base de datos: {str(e)}")

    return {"detail": "Importadad database existosamente"}
