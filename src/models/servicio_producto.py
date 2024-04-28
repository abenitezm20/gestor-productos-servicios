from marshmallow import Schema, fields
from .db import Base
from sqlalchemy import UUID, Column, ForeignKey, Float, Boolean, String, Integer, DateTime, BigInteger
from sqlalchemy.orm import Mapped, relationship
from src.models.model import Model
from src.models.socio_negocio import SocioNegocio
from src.models.subtipo_servicio_producto import SubtipoServicioProducto


class ServicioProducto(Model, Base):
    __tablename__ = "servicio_producto"
    id_socio_negocio = Column(UUID(as_uuid=True), ForeignKey('socio_negocio.id'), primary_key=True)
    id_deporte = Column(UUID(as_uuid=True))
    id_subtipo_servicio_producto = Column(UUID(as_uuid=True), ForeignKey('subtipo_servicio_producto.id'), primary_key=True)

    pais = Column(String(50))
    ciudad = Column(String(50))
    lugar_entrega_prestacion = Column(String(50))
    cantidad_disponible = Column(Integer)
    fecha_entrega_prestacion = Column(DateTime)
    valor = Column(BigInteger)
    descripcion = Column(String(1000))

    socio_negocio: Mapped['SocioNegocio'] = relationship("SocioNegocio", backref="servicio_producto_socio")
    subtipo_servicio_producto: Mapped['SubtipoServicioProducto'] = relationship("SubtipoServicioProducto", backref="servicio_producto_subtipo")

    def __init__(self, id_socio_negocio, id_deporte, id_subtipo_servicio_producto, pais, ciudad, lugar_entrega_prestacion, cantidad_disponible, fecha_entrega_prestacion, valor, descripcion):
        Model.__init__(self)
        self.id_socio_negocio = id_socio_negocio
        self.id_deporte = id_deporte
        self.id_subtipo_servicio_producto = id_subtipo_servicio_producto
        self.pais = pais
        self.ciudad = ciudad
        self.lugar_entrega_prestacion = lugar_entrega_prestacion
        self.cantidad_disponible = cantidad_disponible
        self.fecha_entrega_prestacion = fecha_entrega_prestacion
        self.valor = valor
        self.descripcion = descripcion


class ServicioProductoSchema(Schema):
    id = fields.UUID()
    id_socio_negocio = fields.UUID()
    id_deporte = fields.UUID()
    id_subtipo_servicio_producto = fields.UUID()
    pais = fields.Str()
    ciudad = fields.Str()
    lugar_entrega_prestacion = fields.Str()
    cantidad_disponible = fields.Int()
    fecha_entrega_prestacion = fields.DateTime()
    valor = fields.Int()
    descripcion = fields.Str()