import logging
from flask import Blueprint, jsonify, make_response, request
from src.utils.seguridad_utils import SocioToken, token_required
from src.commands.productos_servicios.agregar_productos_servicios import AgregarProductosServicios
from src.commands.productos_servicios.listar_productos_servicios import ListarProductosServicios

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
        'valor': body.get('valor', None)
    }

    result = AgregarProductosServicios(usuario_token, info).execute()
    return make_response(jsonify(result), 200)


@productos_servicios_blueprint.route('/listar', methods=['GET'])
@token_required
def listar_productos_servicios(usuario_token: SocioToken):
    logger.info(f'Listar productos de {usuario_token.email}')
    #body = request.get_json()

    info = {
        'email': usuario_token.email,
    }

    result = ListarProductosServicios(usuario_token, info).execute()
    return make_response(jsonify(result), 200)