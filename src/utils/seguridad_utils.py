import os
import logging
import requests
from functools import wraps
from flask import request

from src.errors.errors import ApiError, TokenNotFound, Unauthorized

HEADER_NAME = 'Authorization'
URL_AUTORIZADOR = os.getenv(
    'URL_AUTORIZADOR', 'http://127.0.0.1:3000')
URL_VALIDAR_TOKEN = URL_AUTORIZADOR + '/autorizador/seguridad/validar-token'
URL_GENERAR_TOKEN = URL_AUTORIZADOR + '/autorizador/seguridad/generar-token'
TOKEN_INVALIDO = 'Token invalido'

logger = logging.getLogger(__name__)


def token_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        token_bearer = request.headers.get(HEADER_NAME)
        logger.info(f'Validando token {token_bearer}')

        if token_bearer is None:
            raise TokenNotFound

        #email = None
        deportista: DeportistaToken = None
        token = token_bearer.split(' ')[1]
        logger.info(f'URL {URL_VALIDAR_TOKEN}')

        try:
            response = requests.post(
                url=URL_VALIDAR_TOKEN, json={"token": token})

            if response.status_code == 200:
                data = response.json()

                if data['token_valido'] is False:
                    logger.error(TOKEN_INVALIDO)
                    raise Unauthorized

                logger.info('Token valido')
                deportista = DeportistaToken(
                    email=data['email'],
                    subscripcion=data['subscripcion'],
                    tipo_usuario=data['tipo_usuario'],
                )
                #email = data['email']
            else:
                logger.error(TOKEN_INVALIDO)
                raise Unauthorized

        except Exception as e:
            logging.error(f'Error validando token con el autorizador {e}')
            raise Unauthorized

        #return func(email, *args, **kwargs)
        return func(deportista, *args, **kwargs)
    return wrapper


def get_token(email: str, tipo_usuario: str = None, subscripcion: str = None):
    logger.info(f'Obteniendo token para {email}')
    logger.info(f'URL {URL_GENERAR_TOKEN}')
    try:
        response = requests.post(
            url=URL_GENERAR_TOKEN, json={"email": email, "subscripcion": subscripcion, "tipo_usuario": tipo_usuario})

        if response.status_code == 200:
            data = response.json()

            if data['token'] is None:
                logger.error(TOKEN_INVALIDO)
                raise ApiError

            return data['token']
        else:
            logger.error('Credenciales invalidas')
            raise Unauthorized

    except Exception as e:
        logger.error(f'Error obteniendo token con el autorizador {e}')
        raise ApiError

class DeportistaToken():
    def __init__(self, email: str, subscripcion: str, tipo_usuario: str):
        self.email = email
        self.subscripcion = subscripcion
        self.tipo_usuario = tipo_usuario