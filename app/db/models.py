from sqlalchemy import Column, Integer, String, Text, DateTime, Time, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum
from datetime import datetime

# 🔸 Enum para entradas o salidas
class TipoRegistroEnum(enum.Enum):
    entrada = "entrada"
    salida = "salida"

# 🔸 Tabla: personal
class Personal(Base):
    __tablename__ = "personal"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    documento = Column(String(50), unique=True, nullable=False)
    cargo = Column(String(100))
    email = Column(String(100))
    encoding = Column(Text(length=4294967295), nullable=False)  # LONGTEXT
    hora_entrada_establecida = Column(Time, nullable=False)
    hora_salida_establecida = Column(Time, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    registros = relationship("RegistroIngreso", back_populates="personal")

# 🔸 Tabla: registro_ingresos
class RegistroIngreso(Base):
    __tablename__ = "registro_ingresos"

    id = Column(Integer, primary_key=True, index=True)
    id_personal = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(Enum(TipoRegistroEnum), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)

    personal = relationship("Personal", back_populates="registros")
