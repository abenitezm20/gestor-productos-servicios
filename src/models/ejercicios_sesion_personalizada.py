from .db import Base
from sqlalchemy import UUID, Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, relationship
from src.models.model import Model
from src.models.sesion_personalizada import SesionPersonalizada


class EjerciciosSesionPersonalizada(Model, Base):
    __tablename__ = "ejercicios_sesion_personalizada"
    nombre = Column(String(50))
    id_sesion_personalizada = Column(UUID(as_uuid=True), ForeignKey('sesion_personalizada.id'), primary_key=True)
    descripcion = Column(String(300))
    cantidad_repeticiones = Column(Integer)
    duracion = Column(Integer)

    sesion_personalizada: Mapped['SesionPersonalizada'] = relationship("SesionPersonalizada", backref="ejercicios_sesion")


    def __init__(self, nombre, id_sesion_personalizada, descripcion, cantidad_repeticiones, duracion):
        Model.__init__(self)
        self.nombre = nombre
        self.id_sesion_personalizada = id_sesion_personalizada
        self.descripcion = descripcion
        self.cantidad_repeticiones = cantidad_repeticiones
        self.duracion = duracion
