import logging

from src.commands.base_command import BaseCommand
from src.errors.errors import BadRequest
from src.models.db import db_session
from src.models.deportista import Deportista
from src.models.fotos import Fotos
from src.models.servicio_producto import ServicioProducto, ServicioProductoSchema
from src.models.deporte import Deporte
from src.models.servicio_producto_deportista import ServicioProductoDeportista
from src.models.socio_negocio import SocioNegocio
from src.models.subtipo_servicio_producto import SubtipoServicioProducto
from src.utils.seguridad_utils import SocioToken
from src.utils.str_utils import str_none_or_empty
from sqlalchemy import text 

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
        with db_session() as session:
            #socio_negocio: SocioNegocio = SocioNegocio.query.filter_by(email=self.usuario_token.email).first()
            socio_negocio: SocioNegocio = session.query(SocioNegocio).filter_by(email=self.usuario_token.email).first()
    
            if socio_negocio is None:
                logger.error("Socio de Negocio No Existe")
                raise BadRequest
            else:
                logger.info(f"Listando Productos de: {socio_negocio.email}")
                #servicios: ServicioProducto = ServicioProducto.query.filter_by(id_socio_negocio=socio_negocio.id).all()
                servicios = session.query(ServicioProducto).filter(ServicioProducto.id_socio_negocio==socio_negocio.id).all()

                if servicios is None:
                    logger.error("Servicios o Productos No Existen para este socio de negocio")
                    raise BadRequest
                else:
                    response = []
                    for servicio in servicios:

                        #deporte: Deporte = Deporte.query.filter_by(id=servicio.id_deporte).first()
                        deporte = session.query(Deporte).filter(Deporte.id == servicio.id_deporte).first()

                        #subtipo_servicio_producto: SubtipoServicioProducto = SubtipoServicioProducto.query.filter_by(id=servicio.id_subtipo_servicio_producto).first()
                        subtipo_servicio_producto = session.query(SubtipoServicioProducto).filter(SubtipoServicioProducto.id == servicio.id_subtipo_servicio_producto).first()

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
                            'fotos': []
                        }

                        #fotos = Fotos.query.filter(Fotos.id_servicio_producto == servicio.id).all()
                        fotos = session.query(Fotos).filter(Fotos.id_servicio_producto == servicio.id).all()
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


class ListarProductosServiciosFiltro (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Buscar productos y servicios a usuario deportista')

        self.usuario_token: SocioToken = usuario_token
        self.info = info
        self.filtros = []

        #se valida la accion a realizar
        if self.info.get('accion') is not None:
            self.filtros = (self.info.get('accion')).split('|')

        if str_none_or_empty(info.get('email')):
            logger.error("email no puede ser vacio o nulo")
            raise BadRequest


    def execute(self):
        with db_session() as session:
            #socio_negocio: SocioNegocio = SocioNegocio.query.filter_by(email=self.usuario_token.email).first()
            socio_negocio: SocioNegocio = session.query(SocioNegocio).filter_by(email=self.usuario_token.email).first()
        
            if socio_negocio is None:
                logger.error("Socio de Negocio No Existe")
                raise BadRequest
            else:
                logger.info(f"Listando Productos de: {socio_negocio.email}")

                #se empiezan a aplicar los filtros
                if self.filtros.__len__() > 0:

                    #Se genera filtro base para la consulta
                    queryFilter = """SELECT sp.cantidad_disponible, sp.ciudad, sp.descripcion, sp.fecha_entrega_prestacion, sp.id, d.nombre as deporte, sp.id_socio_negocio, ssp.nombre as subtipo, ssp.tipo as tipo, sp.lugar_entrega_prestacion, sp.pais, sp.valor,
                                    (select count(1) as vendidos from servicio_producto_deportista spd where spd.id_servicio_producto = sp.id)
                                    FROM servicio_producto sp, subtipo_servicio_producto ssp, deporte d  
                                    WHERE sp.id_socio_negocio = '""" + str(socio_negocio.id) + """'
                                    and sp.id_subtipo_servicio_producto  = ssp.id
                                    and sp.id_deporte = d.id"""
                    flagProducto = False
                    flagServicio = False
                    flagAmbos = False
                    flagAtletismo = False
                    flagCiclismo = False
                    flagVendidos = False 
                    for filtro in self.filtros:
                        if filtro == "producto":
                            if flagServicio == False:
                                flagProducto = True
                                flagAmbos = False
                            else:
                                flagAmbos = True
                                queryFilter = queryFilter + " and ssp.tipo IN ('servicio','producto')"
                        elif filtro == "servicio":
                            if flagProducto == False:
                                flagServicio = True
                                flagAmbos = False
                            else:
                                flagAmbos = True
                                queryFilter = queryFilter + " and ssp.tipo IN ('servicio','producto')"
                        elif filtro == "Ciclismo":
                            flagCiclismo = True
                            queryFilter = queryFilter + " and d.nombre = 'Ciclismo'"
                        elif filtro == "Atletismo":
                            flagAtletismo = True
                            queryFilter = queryFilter + " and d.nombre = 'Atletismo'"
                        elif filtro == "vendidos":
                            flagVendidos = True
                            queryFilter = queryFilter + " and (select count(1) as vendidos from servicio_producto_deportista spd where spd.id_servicio_producto = sp.id) > 0"

                    if flagAmbos == False:
                        if flagProducto == True:
                            queryFilter = queryFilter + " and ssp.tipo = 'producto'"
                        elif flagServicio == True:
                            queryFilter = queryFilter + " and ssp.tipo = 'servicio'"

                    print ("Query: ", queryFilter)

                    sqlQuery = text(queryFilter)
                    servicios = session.execute(sqlQuery)

                    if servicios is None:
                        logger.error("Servicios o Productos No Existen para este socio de negocio")
                        raise BadRequest
                    else:
                        response = []
                        for servicio in servicios:

                            responseServicio = {
                                'cantidad_disponible': servicio.cantidad_disponible,
                                'ciudad': servicio.ciudad,
                                'descripcion': servicio.descripcion,
                                'fecha_entrega_prestacion': servicio.fecha_entrega_prestacion,
                                'id': servicio.id,
                                'deporte': servicio.deporte,
                                'id_socio_negocio': servicio.id_socio_negocio,
                                'subtipo_servicio_producto': servicio.subtipo,
                                'tipo_servicio_producto': servicio.tipo,
                                'lugar_entrega_prestacion': servicio.lugar_entrega_prestacion,
                                'pais': servicio.pais,
                                'valor': servicio.valor,
                                'vendidos': servicio.vendidos,
                                'fotos': []
                            }

                            #fotos = Fotos.query.filter(Fotos.id_servicio_producto == servicio.id).all()
                            fotos = session.query(Fotos).filter(Fotos.id_servicio_producto == servicio.id).all()
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


class ListarProductosServiciosID (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Buscar productos y servicios por un ID especifico')

        self.usuario_token: SocioToken = usuario_token
        self.info = info

        if str_none_or_empty(info.get('email')):
            logger.error("email no puede ser vacio o nulo")
            raise BadRequest


    def execute(self):
        with db_session() as session:
            #socio_negocio: SocioNegocio = SocioNegocio.query.filter_by(email=self.usuario_token.email).first()
            socio_negocio: SocioNegocio = session.query(SocioNegocio).filter_by(email=self.usuario_token.email).first()

            if socio_negocio is None:
                logger.error("Socio de Negocio No Existe")
                raise BadRequest
            else:
                logger.info(f"Listando Productos de: {socio_negocio.email}")
                #servicios: ServicioProducto = ServicioProducto.query.filter_by(id=self.info.get('id')).all()
                servicios = session.query(ServicioProducto).filter(ServicioProducto.id == self.info.get('id')).all()

                if servicios is None:
                    logger.error("Servicios o Productos No Existen para este socio de negocio")
                    raise BadRequest
                else:
                    response = []
                    for servicio in servicios:

                        #deporte: Deporte = Deporte.query.filter_by(id=servicio.id_deporte).first()
                        deporte = session.query(Deporte).filter(Deporte.id == servicio.id_deporte).first()

                        #subtipo_servicio_producto: SubtipoServicioProducto = SubtipoServicioProducto.query.filter_by(id=servicio.id_subtipo_servicio_producto).first()
                        subtipo_servicio_producto = session.query(SubtipoServicioProducto).filter(SubtipoServicioProducto.id == servicio.id_subtipo_servicio_producto).first()

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
                            'fotos': []
                        }

                        #fotos = Fotos.query.filter(Fotos.id_servicio_producto == servicio.id).all()
                        fotos = session.query(Fotos).filter(Fotos.id_servicio_producto == servicio.id).all()
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
            

            
class ListarCompradores (BaseCommand):
    def __init__(self, usuario_token: SocioToken, info: dict):
        logger.info(
            'Listar Compradores por ID especifico')

        self.usuario_token: SocioToken = usuario_token
        self.info = info

        if str_none_or_empty(info.get('email')):
            logger.error("email no puede ser vacio o nulo")
            raise BadRequest


    def execute(self):
        with db_session() as session:
            #socio_negocio: SocioNegocio = SocioNegocio.query.filter_by(email=self.usuario_token.email).first()
            socio_negocio = session.query(SocioNegocio).filter(SocioNegocio.email == self.usuario_token.email).first()
        
            if socio_negocio is None:
                logger.error("Socio de Negocio No Existe")
                raise BadRequest
            else:
                logger.info(f"Listando Productos de: {socio_negocio.email}")
                logger.info(f"El servicio a buscar es: {self.info.get('id_servicio_producto')}")
                servicios: ServicioProductoDeportista = session.query(ServicioProductoDeportista).filter(ServicioProductoDeportista.id_servicio_producto == self.info.get('id_servicio_producto')).all()

                if servicios is None:
                    logger.error("Servicios o Productos No Existen para este socio de negocio")
                    raise BadRequest
                else:
                    response = []
                    for servicio in servicios:

                        deportista: Deportista = session.query(Deportista).filter(Deportista.id == servicio.id_deportista).first()

                        responseServicio = {
                            'deportista_nombre': deportista.nombre+' '+deportista.apellido,
                            'deportista_numero_identificacion': deportista.numero_identificacion,
                            'servicio_producto_deportista_direccion_servicio': servicio.direccion_servicio,
                            'servicio_producto_deportista_telefono': servicio.telefono,
                            'servicio_producto_deportista_metodo_pago': servicio.metodo_pago,
                            'servicio_producto_deportista_estado_entrega': servicio.estado_entrega,
                            'servicio_producto_deportista_fecha_servicio': servicio.fecha_servicio,
                        }
                
                        response.append(responseServicio)
                
                    return response