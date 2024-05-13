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


class ListarProductosServiciosDeportistaID (BaseCommand):
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
                servicios: ServicioProducto = ServicioProducto.query.filter_by(id=self.info.get('id')).all()

                if servicios is None:
                    logger.error("Servicios o Productos Vigentes No Existentes")
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
                

class ListarProductosServiciosDeportistaFiltro (BaseCommand):
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
            deportista: Deportista = Deportista.query.filter_by(email=self.usuario_token.email).first()
        
            if deportista is None:
                logger.error("Deportista No Existe")
                raise BadRequest
            else:
                logger.info(f"Listando Productos de: {deportista.email}")

                #se empiezan a aplicar los filtros
                if self.filtros.__len__() > 0:

                    #Se genera filtro base para la consulta
                    queryFilter = """SELECT sp.cantidad_disponible, sp.ciudad, sp.descripcion, sp.fecha_entrega_prestacion, sp.id, d.nombre as deporte, sp.id_socio_negocio, ssp.nombre as subtipo, ssp.tipo as tipo, sp.lugar_entrega_prestacion, sp.pais, sp.valor
                                    FROM servicio_producto sp, subtipo_servicio_producto ssp, deporte d  
                                    WHERE sp.id_subtipo_servicio_producto  = ssp.id
                                    and sp.fecha_entrega_prestacion >= '""" + str(date.today()) + """'
                                    and sp.id_deporte = d.id"""
                    flagProducto = False
                    flagServicio = False
                    flagAmbos = False
                    flagAtletismo = False
                    flagCiclismo = False
                    servicio_producto_comprados = 0
                    flagSelecionoServiciosPropios = False
                    flagTieneServiciosPropios = False
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
                        elif filtro == "propios":
                            flagSelecionoServiciosPropios = True
                            queryPropios = """SELECT spd.id_servicio_producto
                                FROM servicio_producto sp, subtipo_servicio_producto ssp, deporte d, servicio_producto_deportista spd  
                                WHERE sp.id_subtipo_servicio_producto  = ssp.id
                                and sp.id_deporte = d.id
                                and sp.id = spd.id_servicio_producto 
                                and ssp.tipo IN ('servicio','producto')
                                and spd.id_deportista = '""" + str(deportista.id) + """'
                                group by spd.id_servicio_producto"""
                            print ("queryPropios: ", queryPropios)
                            sqlQueryPropios = text(queryPropios)
                            serviciosPropios = session.execute(sqlQueryPropios)
                            primerregistro = True     
                            for servicio in serviciosPropios:
                                flagTieneServiciosPropios = True
                                if primerregistro == True:
                                    queryFilter = queryFilter + " and sp.id IN (" + "'" + str(servicio.id_servicio_producto) + "'"
                                elif primerregistro == False:
                                    queryFilter = queryFilter + "," + "'" + str(servicio.id_servicio_producto) + "'"
                                primerregistro = False
                            if primerregistro == False:
                                queryFilter = queryFilter + ")"

                    if flagAmbos == False:
                        if flagProducto == True:
                            queryFilter = queryFilter + " and ssp.tipo = 'producto'"
                        elif flagServicio == True:
                            queryFilter = queryFilter + " and ssp.tipo = 'servicio'"

                    print ("Query: ", queryFilter)
                    
                    if flagSelecionoServiciosPropios == True and flagTieneServiciosPropios == False:
                        return []
                    else:
                        sqlQuery = text(queryFilter)
                        servicios = session.execute(sqlQuery)

                        if servicios is None:
                            logger.error("Servicios o Productos No Existen para este socio de negocio")
                            raise BadRequest
                        else:
                            response = []
                            for servicio in servicios:
                                queryComprados = """SELECT count(1) as cantidad_comprada
                                        FROM servicio_producto_deportista spd  
                                        WHERE spd.id_deportista = '""" + str(deportista.id) + """'
                                        AND spd.id_servicio_producto = '""" + str(servicio.id) + """'"""
                                sqlQueryComprados = text(queryComprados)
                                servicio_producto_comprados = session.execute(sqlQueryComprados).fetchone().cantidad_comprada
                                #print("Servicios Comprados: ", str(servicio_producto_comprados))

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
                                    'servicio_producto_comprados': servicio_producto_comprados,
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

