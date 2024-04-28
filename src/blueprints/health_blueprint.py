import os
import logging
from flask import Blueprint, jsonify, make_response
from src.commands.health_check.health import Health

VERSION = os.getenv('VERSION')

logger = logging.getLogger(__name__)
health_blueprint = Blueprint('health', __name__)


@health_blueprint.route('/ping', methods=['GET'])
def health():
    logger.info('Versión de la aplicación %s', VERSION)
    result = Health().execute()
    return make_response(jsonify({'result': result}), 200)
