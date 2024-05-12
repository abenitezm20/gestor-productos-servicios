import logging
from flask import Blueprint, jsonify, make_response, request
from src.utils.seguridad_utils import SocioToken, token_required
from src.commands.productos_servicios_deportista.listar_productos_servicios_deportista import ListarProductosServiciosDeportista, ListarProductosServiciosDeportistaFiltro
from src.commands.productos_servicios_deportista.adquirir_productos_servicios_deportistas import AdquirirProductosServiciosDeportista

logger = logging.getLogger(__name__)
productos_servicios_deportista_blueprint = Blueprint('productos-servicios-deportista', __name__)


@productos_servicios_deportista_blueprint.route('/listar', methods=['GET'])
@token_required
def listar_productos_servicios(usuario_token: SocioToken):
    logger.info(f'Listar productos de {usuario_token.email}')
    info = {
        'email': usuario_token.email,

    }
    result = ListarProductosServiciosDeportista(usuario_token, info).execute()
    return make_response(jsonify(result), 200)


@productos_servicios_deportista_blueprint.route('/comprar', methods=['POST'])
@token_required
def comprar_productos_servicios(usuario_token: SocioToken):
    logger.info(f'Listar productos de {usuario_token.email}')
    body = request.get_json()
    info = {
        'email': usuario_token.email,
        'id_servicio_producto': body.get('id_servicio_producto', None),
        'fecha_servicio': body.get('fecha_servicio', None),
        'direccion_servicio': body.get('direccion_servicio', None),
        'valor': body.get('valor', None),
        'telefono': body.get('telefono', None),
        'metodo_pago': body.get('metodo_pago', None),
        'estado_entrega': body.get('estado_entrega', None)
    }
    result = AdquirirProductosServiciosDeportista(usuario_token, info).execute()
    return make_response(jsonify(result), 200)


#Esta accion se utiliza como filtrar, ya sea por producto, servicio o deporte.
@productos_servicios_deportista_blueprint.route('/listar/<accion>', methods=['GET'])
@token_required
def listar_productos_servicios_filtro(usuario_token: SocioToken, accion: str):
    logger.info(f'Listar productos de {usuario_token.email}')
    if accion is not None:
        info = {
            'email': usuario_token.email,
            'accion': accion,
        }
        result = ListarProductosServiciosDeportistaFiltro(usuario_token, info).execute()
    return make_response(jsonify(result), 200)