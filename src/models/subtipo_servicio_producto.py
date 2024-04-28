import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Enum, String, Float, BigInteger
from .model import Model
from .db import Base


class TipoServicioProductoEnum(str, enum.Enum):
    producto = "producto"
    servicio = "servicio"


class SubtipoServicioProducto(Model, Base):
    __tablename__ = "subtipo_servicio_producto"
    nombre = Column(String(50))
    tipo= Column(Enum(TipoServicioProductoEnum))



    def __init__(self, nombre, tipo):
        Model.__init__(self)
        self.nombre = nombre
        self.tipo = tipo