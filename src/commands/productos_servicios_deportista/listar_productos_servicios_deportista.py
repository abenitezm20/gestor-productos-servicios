import logging
from sqlalchemy import Date, cast
from datetime import date
from src.commands.base_command import BaseCommand
from src.errors.errors import BadRequest
from src.models.db import db_session
from src.models.deportista import Deportista
from src.models.fotos import Fotos
from src.models.servicio_producto import ServicioProducto, ServicioProductoSchema
from src.models.deporte import Deporte
from src.models.servicio_producto_deportista import ServicioProductoDeportista
from src.models.subtipo_servicio_producto import SubtipoServicioProducto
from src.utils.seguridad_utils import SocioToken
from src.utils.str_utils import str_none_or_empty
from sqlalchemy import text 

logger = logging.getLogger(__name__)


class ListarProductosServiciosDeportista (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Buscar productos y servicios a usuario deportista')

        self.usuario_token: SocioToken = usuario_token
        self.info = info

        if str_none_or_empty(info.get('email')):
            logger.error("email no puede ser vacio o nulo")
            raise BadRequest


    def execute(self):
        deportista: Deportista = Deportista.query.filter_by(email=self.usuario_token.email).first()
        with db_session() as session:        
            if deportista is None:
                logger.error("Deportista No Existe")
                raise BadRequest
            else:
                logger.info(f"Listando Todos los Productos para: {deportista.email}")
                servicios: ServicioProducto = session.query(ServicioProducto).filter(cast(ServicioProducto.fecha_entrega_prestacion, Date) >= date.today()).all()

                if servicios is None:
                    logger.error("Servicios o Productos No Existen para este socio de negocio")
                    raise BadRequest
                else:
                    response = []
                    for servicio in servicios:

                        servicio_producto_vendidos: ServicioProductoDeportista = ServicioProductoDeportista.query.filter_by(id_servicio_producto=servicio.id).all()

                        deporte: Deporte = Deporte.query.filter_by(id=servicio.id_deporte).first()

                        subtipo_servicio_producto: SubtipoServicioProducto = SubtipoServicioProducto.query.filter_by(id=servicio.id_subtipo_servicio_producto).first()

                        responseServicio = {
                            'cantidad_disponible': servicio.cantidad_disponible,
                            'ciudad': servicio.ciudad,
                            'descripcion': servicio.descripcion,
                            'fecha_entrega_prestacion': servicio.fecha_entrega_prestacion,
                            'id': servicio.id,
                            'deporte': deporte.nombre,
                            'id_socio_negocio': servicio.id_socio_negocio,
                            'subtipo_servicio_producto': subtipo_servicio_producto.nombre,
                            'tipo_servicio_producto': subtipo_servicio_producto.tipo,
                            'lugar_entrega_prestacion': servicio.lugar_entrega_prestacion,
                            'pais': servicio.pais,
                            'valor': servicio.valor,
                            'servicio_producto_vendidos': len(servicio_producto_vendidos),
                            'fotos': []
                        }

                        fotos = Fotos.query.filter(Fotos.id_servicio_producto == servicio.id).all()
                        if fotos is not None:
                            for recfoto in fotos:
                                responseServicio['fotos'].append({
                                    'orden': recfoto.orden,
                                    'foto': recfoto.foto
                                })
                        else:
                            print("No hay fotos")
                
                        response.append(responseServicio)
                
                    return response


