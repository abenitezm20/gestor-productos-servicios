import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Enum, String, Float, BigInteger
from .model import Model
from .db import Base


class TipoIdentificacionSocioEnum(str, enum.Enum):
    tarjeta_identidad = "tarjeta_identidad"
    cedula_ciudadania = "cedula_ciudadania"
    cedula_extranjeria = "cedula_extranjeria"
    pasaporte = "pasaporte"
    registro_civil = "registro_civil"
    nit = "nit"


class SocioNegocio(Model, Base):
    __tablename__ = "socio_negocio"
    nombre = Column(String(50))
    tipo_identificacion = Column(Enum(TipoIdentificacionSocioEnum))
    numero_identificacion = Column(String(50))                                
    email = Column(String(50), unique=True)
    contrasena = Column(String(50))


    def __init__(self, nombre, tipo_identificacion, numero_identificacion, email, contrasena):
        Model.__init__(self)
        self.nombre = nombre
        self.tipo_identificacion = tipo_identificacion
        self.numero_identificacion = numero_identificacion
        self.email = email
        self.contrasena = contrasena
        