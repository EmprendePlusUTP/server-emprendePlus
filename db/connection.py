from sqlmodel import SQLModel, create_engine

# Definir el nombre del archivo; se recomienda usar la extensión .db para la base de datos SQLite
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Crear el engine; echo=True permitirá ver las consultas SQL en la consola
engine = create_engine(sqlite_url, echo=True)

def init_db():
    """
    Importa los modelos y crea todas las tablas en la base de datos.
    """
    import models  # Esto importa tu archivo models.py para registrar todos los modelos en SQLModel.metadata
    SQLModel.metadata.create_all(engine)