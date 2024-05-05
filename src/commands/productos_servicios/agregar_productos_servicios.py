import datetime
import logging

from src.commands.base_command import BaseCommand
from src.errors.errors import BadRequest
from src.models.db import db_session
from src.models.deporte import Deporte
from src.models.fotos import Fotos
from src.models.servicio_producto import ServicioProducto
from src.models.socio_negocio import SocioNegocio
from src.models.subtipo_servicio_producto import SubtipoServicioProducto
from src.utils.seguridad_utils import SocioToken
from src.utils.str_utils import str_none_or_empty


logger = logging.getLogger(__name__)


class AgregarProductosServicios(BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Agregar productos a usuario deportista')

        self.usuario_token: SocioToken = usuario_token
        self.info = info

        if str_none_or_empty(info.get('email')):
            logger.error("email no puede ser vacio o nulo")
            raise BadRequest

    def execute(self):
        with db_session() as session:
            socio_negocio: SocioNegocio = SocioNegocio.query.filter_by(email=self.usuario_token.email).first()
        
            if socio_negocio is None:
                logger.error("Socio de Negocio No Existe")
                raise BadRequest
            else:
                logger.info(f"Registrando Productos y Servicio para: {socio_negocio.email}")
                id_subtipo_servicio_producto = None

                #Primero se almacena la informacion del producto o servicio
                subtipo_servicio_producto = SubtipoServicioProducto.query.filter_by(
                    nombre=self.info.get('subtipo'),
                    tipo=self.info.get('tipo')
                    ).first()
                
                #Si no existe el subtipo_servicio_producto se crea
                if subtipo_servicio_producto is None:
                    rec_subtipo_servicio_producto = SubtipoServicioProducto(nombre=self.info.get('subtipo'), 
                                                                            tipo=self.info.get('tipo'))
                    session.add(rec_subtipo_servicio_producto)
                    session.commit()
                    
                    subtipo_servicio_producto_interno = SubtipoServicioProducto.query.filter_by(nombre=self.info.get('subtipo'), tipo=self.info.get('tipo')).first()
                    id_subtipo_servicio_producto = subtipo_servicio_producto_interno.id
                else:
                    id_subtipo_servicio_producto = subtipo_servicio_producto.id


                #se consulta el id del deporte
                deporte = Deporte.query.filter(Deporte.nombre == self.info.get('deporte')).first()
    
                record = ServicioProducto(id_socio_negocio=socio_negocio.id,
                                                    id_deporte=deporte.id,
                                                    id_subtipo_servicio_producto=id_subtipo_servicio_producto,
                                                    pais=self.info.get('pais'),
                                                    ciudad=self.info.get('ciudad'),
                                                    lugar_entrega_prestacion=self.info.get('lugar_entrega_prestacion'),
                                                    cantidad_disponible=self.info.get('cantidad_disponible'),
                                                    fecha_entrega_prestacion=self.info.get('fecha_entrega_prestacion'),
                                                    valor=self.info.get('valor'),
                                                    descripcion=self.info.get('descripcion'))


                session.add(record)
                session.commit()

                #se consulta el id del servicio o producto creado
                servicio_producto = ServicioProducto.query.filter(ServicioProducto.id_socio_negocio == socio_negocio.id,
                                                                  ServicioProducto.descripcion == self.info.get('descripcion')).first()

                if servicio_producto is None:
                    logger.error("Servicio o Producto No Existe")
                    raise BadRequest
                else:
                    #se almacenan las fotos del servicio o producto
                    if self.info.get('fotos') is not None:
                        for fotos in self.info.get('fotos'):
                            rec_foto = Fotos(id_servicio_producto=servicio_producto.id, 
                                            foto= fotos.get('foto'),
                                            orden=fotos.get('orden'))
                            session.add(rec_foto)
                            session.commit()

                response = {
                    'message': 'success',
                    'id_servicio_producto': servicio_producto.id
                }

            return response
