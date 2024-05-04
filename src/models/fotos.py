from .db import Base
from sqlalchemy import UUID, Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, relationship
from src.models.model import Model
from src.models.servicio_producto import ServicioProducto


class Fotos(Model, Base):
    __tablename__ = "fotos"
    foto = Column(String(100000))
    orden = Column(Integer)
    id_servicio_producto = Column(UUID(as_uuid=True))

    def __init__(self, foto, orden, id_servicio_producto):
        Model.__init__(self)
        self.foto = foto
        self.id_servicio_producto = id_servicio_producto
        self.orden = orden