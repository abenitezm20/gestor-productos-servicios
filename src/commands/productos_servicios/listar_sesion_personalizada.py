import logging

from src.commands.base_command import BaseCommand
from src.errors.errors import BadRequest
from src.models.db import db_session
from src.models.ejercicios_sesion_personalizada import EjerciciosSesionPersonalizada
from src.models.servicio_producto import ServicioProducto, ServicioProductoSchema
from src.models.sesion_personalizada import SesionPersonalizada
from src.models.socio_negocio import SocioNegocio
from src.utils.seguridad_utils import SocioToken
from src.utils.str_utils import str_none_or_empty

logger = logging.getLogger(__name__)


class ListarSesionPersonalizada (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Buscar Sesion Personalizada')

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
            logger.info(f"Sesiones Personalizadas de: {socio_negocio.email}")

            #se consultan las sesiones personalizadas con el ID de servicio producto
            sesion_personalizada = SesionPersonalizada.query.filter(SesionPersonalizada.id_servicio_producto == self.info.get('id_servicio_producto')).first()
            if sesion_personalizada is None:
                logger.error("Sesiones Personalizadas No Existen para este socio de negocio")
                raise BadRequest
            else:
                response = {
                    'nombre_sesion': sesion_personalizada.nombre,
                    'id_servicio_producto': sesion_personalizada.id_servicio_producto,
                    'ejercicios': []
                }

                ejercicios = EjerciciosSesionPersonalizada.query.filter(EjerciciosSesionPersonalizada.id_sesion_personalizada == sesion_personalizada.id).all()
                for ejercicio in ejercicios:
                    response['ejercicios'].append({
                        'nombre': ejercicio.nombre,
                        'descripcion': ejercicio.descripcion,
                        'cantidad_repeticiones': ejercicio.cantidad_repeticiones,
                        'duracion': ejercicio.duracion
                    })
                return response