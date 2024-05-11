import logging
from src.commands.base_command import BaseCommand
from src.errors.errors import BadRequest
from src.models.db import db_session
from src.models.deportista import Deportista
from src.models.servicio_producto import ServicioProducto
from src.models.servicio_producto_deportista import ServicioProductoDeportista
from src.utils.seguridad_utils import SocioToken
from src.utils.str_utils import str_none_or_empty

logger = logging.getLogger(__name__)

class AdquirirProductosServiciosDeportista (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Comprar productos y servicios a usuario deportista')

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
                logger.info(f"Comprando Productos para: {deportista.email}")

                #validando que el producto exista
                servicio_producto: ServicioProducto = session.query(ServicioProducto).filter_by(id=self.info.get('id_servicio_producto')).first()

                if servicio_producto is None:
                    logger.error("Producto No Existe")
                    raise BadRequest
                else:
                    logger.info(f"Producto Encontrado: {servicio_producto.id}")

                    #validando que el producto tenga disponibilidad
                    servicio_producto_deportista: ServicioProductoDeportista = session.query(ServicioProductoDeportista).filter_by(id_servicio_producto=servicio_producto.id).all()

                    cantidad_comprada = 0

                    for _ in servicio_producto_deportista:
                        cantidad_comprada += 1

                    if cantidad_comprada >= servicio_producto.cantidad_disponible:
                        logger.error("Producto No Disponible")
                        raise BadRequest
                    else:
                        #Comprando producto
                        servicio_producto_deportista = ServicioProductoDeportista(deportista.id, servicio_producto.id, self.info.get('fecha_servicio'), self.info.get('direccion_servicio'), self.info.get('valor'), self.info.get('telefono'), self.info.get('metodo_pago'), self.info.get('estado_entrega'))
                        session.add(servicio_producto_deportista)
                        session.commit()

                    return {
                        'mensaje': 'Producto Comprado'
                    }