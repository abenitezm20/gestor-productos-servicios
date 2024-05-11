from marshmallow import Schema, fields
from .db import Base
from sqlalchemy import UUID, Column, ForeignKey, String, Enum, DateTime, BigInteger
from sqlalchemy.orm import Mapped, relationship
from src.models.model import Model
from src.models.deportista import Deportista
from src.models.servicio_producto import ServicioProducto
import enum

class MetodoEnum(str, enum.Enum):
    efectivo = "efectivo"
    tarjeta = "tarjeta"
    transferencia = "transferencia"

class EstadoEnum(str, enum.Enum):
    entregado = "entregado"
    pendiente = "pendiente"
    cancelado = "cancelado"


class ServicioProductoDeportista(Model, Base):
    __tablename__ = "servicio_producto_deportista"
    id_deportista = Column(UUID(as_uuid=True), ForeignKey('deportista.id'), primary_key=True)
    id_servicio_producto = Column(UUID(as_uuid=True))

    fecha_servicio = Column(DateTime)
    direccion_servicio = Column(String(50))
    valor = Column(BigInteger)
    telefono = Column(String(50))
    metodo_pago = Column(Enum(MetodoEnum))
    estado_entrega = Column(Enum(EstadoEnum))

    deportista: Mapped['Deportista'] = relationship("Deportista", backref="servicio_producto_deportista")
   
    def __init__(self, id_deportista, id_servicio_producto, fecha_servicio, direccion_servicio, valor, telefono, metodo_pago, estado_entrega):
        Model.__init__(self)
        self.id_deportista = id_deportista
        self.id_servicio_producto = id_servicio_producto
        self.fecha_servicio = fecha_servicio
        self.direccion_servicio = direccion_servicio
        self.valor = valor
        self.telefono = telefono
        self.metodo_pago = metodo_pago
        self.estado_entrega = estado_entrega
