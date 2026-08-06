from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "etl_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    estado = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=False), server_default=func.now())

class Sesion(Base):
    __tablename__ = "etl_sesiones"

    id = Column(Integer, primary_key=True, index=True)
    # ondelete="RESTRICT" protege el historial, tal como configuramos en SQL
    user_id = Column(Integer, ForeignKey("etl_users.id", ondelete="RESTRICT"), nullable=False)
    token_sesion = Column(String(255), unique=True, nullable=False)
    ip_terminal = Column(String(45))
    user_agent = Column(Text)
    fecha_conexion = Column(DateTime(timezone=False), server_default=func.now())
    fecha_desconexion = Column(DateTime(timezone=False))
    activa = Column(Boolean, default=True)