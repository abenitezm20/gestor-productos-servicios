import logging

from src.commands.base_command import BaseCommand
from src.errors.errors import BadRequest
from src.models.db import db_session
from src.models.deportista import Deportista
from src.models.ejercicios_sesion_personalizada import EjerciciosSesionPersonalizada
from src.models.sesion_personalizada import SesionPersonalizada
from src.utils.seguridad_utils import SocioToken
from src.utils.str_utils import str_none_or_empty

logger = logging.getLogger(__name__)


class ListarSesionPersonalizadaDeportista (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Buscar Sesion Personalizada')

        self.usuario_token: SocioToken = usuario_token
        self.info = info

        if str_none_or_empty(info.get('email')):
            logger.error("email no puede ser vacio o nulo")
            raise BadRequest


    def execute(self):
        with db_session() as session:
            deportista: Deportista = session.query(Deportista).filter_by(email=self.usuario_token.email).first()
    
            if deportista is None:
                logger.error("Deportista No Existe")
                raise BadRequest
            else:
                logger.info(f"Listando Productos de: {deportista.email}")

                #se consultan las sesiones personalizadas con el ID de servicio producto
                print ("id_servicio_producto: " + self.info.get('id_servicio_producto'))
                sesion_personalizada = SesionPersonalizada.query.filter(SesionPersonalizada.id_servicio_producto == self.info.get('id_servicio_producto')).first()
                if sesion_personalizada is None:
                    logger.error("Sesiones Personalizadas No Existen para este deportista")
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