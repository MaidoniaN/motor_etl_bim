import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cargar variables del archivo .env
load_dotenv()

# Construir la URL de conexión
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear la clase constructora de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para nuestros modelos de base de datos
Base = declarative_base()

# Dependencia para inyectar la sesión de BD en las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()