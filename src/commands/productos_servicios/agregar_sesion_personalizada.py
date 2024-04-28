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


class AgregarsesionPersonalizada(BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Agregar sesion personalizada')

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
            logger.info(f"Agregando Sesiones Personalizadas: {socio_negocio.email}")

            #Primero se almacena la informacion de la sesion personalizada
            rec_sesion_personalizada = SesionPersonalizada(nombre=self.info.get('nombre_sesion'), 
                                                            id_servicio_producto=self.info.get('id_servicio_producto'))
            db_session.add(rec_sesion_personalizada)
            db_session.commit()

            #se consulta el id de la sesion personalizada
            sesion_personalizada = SesionPersonalizada.query.filter(SesionPersonalizada.nombre == self.info.get('nombre_sesion')).first()

            #Se almacenan los ejercicios de la sesion personalizada
            for ejercicio in self.info.get('ejercicios'):
                rec_ejercicio = EjerciciosSesionPersonalizada(nombre=ejercicio.get('nombre'), 
                                                              id_sesion_personalizada=sesion_personalizada.id, 
                                                              descripcion=ejercicio.get('descripcion'), 
                                                              cantidad_repeticiones=ejercicio.get('cantidad_repeticiones'), 
                                                              duracion=ejercicio.get('duracion'))
                db_session.add(rec_ejercicio)
                db_session.commit()
            
            response = {
                'message': 'success'
            }

        return response