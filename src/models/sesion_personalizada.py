from .db import Base
from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship
from src.models.model import Model
from src.models.servicio_producto import ServicioProducto


class SesionPersonalizada(Model, Base):
    __tablename__ = "sesion_personalizada"
    nombre = Column(String(50))
    id_servicio_producto = Column(UUID(as_uuid=True))

    def __init__(self, nombre, id_servicio_producto):
        Model.__init__(self)
        self.nombre = nombre
        self.id_servicio_producto = id_servicio_producto