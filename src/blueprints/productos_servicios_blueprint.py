import logging
from flask import Blueprint, jsonify, make_response, request
from src.utils.seguridad_utils import SocioToken, token_required
from src.commands.productos_servicios.agregar_productos_servicios import AgregarProductosServicios
from src.commands.productos_servicios.listar_productos_servicios import ListarProductosServicios, ListarProductosServiciosFiltro, ListarProductosServiciosID
from src.commands.productos_servicios.agregar_sesion_personalizada import AgregarsesionPersonalizada
from src.commands.productos_servicios.listar_sesion_personalizada import ListarSesionPersonalizada

logger = logging.getLogger(__name__)
productos_servicios_blueprint = Blueprint('productos-servicios', __name__)


@productos_servicios_blueprint.route('/agregar', methods=['POST'])
@token_required
def agregar_productos_servicios(usuario_token: SocioToken):
    logger.info(f'Registrando productos para {usuario_token.email}')
    body = request.get_json()

    info = {
        'email': usuario_token.email,
        'descripcion': body.get('descripcion', None),
        'deporte': body.get('deporte', None),
        'tipo': body.get('tipo', None),
        'subtipo': body.get('subtipo', None),
        'pais': body.get('pais', None),
        'ciudad': body.get('ciudad', None),
        'lugar_entrega_prestacion': body.get('lugar_entrega_prestacion', None),
        'cantidad_disponible': body.get('cantidad_disponible', None),
        'fecha_entrega_prestacion': body.get('fecha_entrega_prestacion', None),
        'valor': body.get('valor', None),
        'fotos': body.get('fotos', None)
    }
    result = AgregarProductosServicios(usuario_token, info).execute()
    return make_response(jsonify(result), 200)


@productos_servicios_blueprint.route('/listar', methods=['GET'])
@token_required
def listar_productos_servicios(usuario_token: SocioToken):
    logger.info(f'Listar productos de {usuario_token.email}')
    info = {
        'email': usuario_token.email,
    }
    result = ListarProductosServicios(usuario_token, info).execute()
    return make_response(jsonify(result), 200)

#Esta accion se utiliza como filtrar, ya sea por producto, servicio o deporte.
@productos_servicios_blueprint.route('/listar/<accion>', methods=['GET'])
@token_required
def listar_productos_servicios_filtro(usuario_token: SocioToken, accion: str):
    logger.info(f'Listar productos de {usuario_token.email}')
    if accion is not None:
        info = {
            'email': usuario_token.email,
            'accion': accion,
        }
        result = ListarProductosServiciosFiltro(usuario_token, info).execute()
    return make_response(jsonify(result), 200)


#Esta accion se utiliza para entregar los detalles por un id indicado
@productos_servicios_blueprint.route('/listarID/<id>', methods=['GET'])
@token_required
def listar_productos_servicios_por_id(usuario_token: SocioToken, id: str):
    logger.info(f'Listar productos de {usuario_token.email}')
    if id is not None:
        info = {
            'email': usuario_token.email,
            'id': id,
        }
        result = ListarProductosServiciosID(usuario_token, info).execute()
    return make_response(jsonify(result), 200)



@productos_servicios_blueprint.route('/agregar-sesion-personalizada', methods=['POST'])
@token_required
def agregar_sesion_personalizada(usuario_token: SocioToken):
    logger.info(f'Agregando sesion personalizada {usuario_token.email}')
    body = request.get_json()

    #Debe llegar el id del servicio o producto al que se asocia esta sesion personalizada
    info = {
        'email': usuario_token.email,
        'id_servicio_producto': body.get('id_servicio_producto', None),
        'nombre_sesion': body.get('nombre_sesion', None),
        'ejercicios': body.get('ejercicios', None),
    }

    result = AgregarsesionPersonalizada(usuario_token, info).execute()
    return make_response(jsonify(result), 200)


@productos_servicios_blueprint.route('/listar-sesion-personalizada/<id>', methods=['GET'])
@token_required
def listar_sesion_personalizada(usuario_token: SocioToken, id: str):
    logger.info(f'Listar ejercicios de sesion personalizada {usuario_token.email}')

    if id is not None:
        info = {
            'email': usuario_token.email,
            'id_servicio_producto' : id
        }
        result = ListarSesionPersonalizada(usuario_token, info).execute()
    return make_response(jsonify(result), 200)