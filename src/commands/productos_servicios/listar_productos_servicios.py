import logging

from src.commands.base_command import BaseCommand
from src.errors.errors import BadRequest
from src.models.db import db_session
from src.models.servicio_producto import ServicioProducto, ServicioProductoSchema
from src.models.socio_negocio import SocioNegocio
from src.utils.seguridad_utils import SocioToken
from src.utils.str_utils import str_none_or_empty

logger = logging.getLogger(__name__)


class ListarProductosServicios (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Buscar productos y servicios a usuario deportista')

        self.usuario_token: SocioToken = usuario_token
        self.info = info

        if str_none_or_empty(info.get('email')):
            logger.error("email no puede ser vacio o nulo")
            raise BadRequest


    def execute(self):
        socio_negocio: SocioNegocio = SocioNegocio.query.filter_by(email=self.usuario_token.email).first()
    
        if socio_negocio is None:
            logger.error("Socio de Negocio No Existe")
            raise BadRequest
        else:
            logger.info(f"Listando Productos de: {socio_negocio.email}")
            servicios: ServicioProducto = ServicioProducto.query.filter_by(id_socio_negocio=socio_negocio.id).all()

            if servicios is None:
                logger.error("Servicios o Productos No Existen para este socio de negocio")
                raise BadRequest
            else:
                response = []
                for servicio in servicios:
                    schema = ServicioProductoSchema()
                    response.append(schema.dump(servicio)) 
                return response
