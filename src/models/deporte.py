from marshmallow import Schema, fields
from .db import Base
from sqlalchemy import Column, String
from src.models.model import Model


class Deporte(Model, Base):
    __tablename__ = "deporte"
    nombre = Column(String(50), unique=True, nullable=False)

    def __init__(self, nombre):
        Model.__init__(self)
        self.nombre = nombre


class DeporteSchema(Schema):
    id = fields.String()
    nombre = fields.String()
