import json
import uuid
import pytest
import logging
from unittest.mock import patch, MagicMock

from faker import Faker
from src.main import app
from src.models.db import db_session
from src.models.deporte import Deporte
from src.models.servicio_producto import ServicioProducto
from src.models.socio_negocio import SocioNegocio, TipoIdentificacionSocioEnum
from sqlalchemy import delete

fake = Faker()
logger = logging.getLogger(__name__)

@pytest.fixture(scope="class")
def setup_data():
    logger.info("Inicio Test Agregar Productos y Servicios")

    # Crear Socio de Negocio
    socio = {
        'nombre':fake.name(),
        'tipo_identificacion':fake.random_element(elements=(
            tipo_identificacion.value for tipo_identificacion in TipoIdentificacionSocioEnum)),
        'numero_identificacion':fake.random_int(min=1000000, max=999999999),
        'email':fake.email(),
        'contrasena':fake.password()
    }
    
    socio_random: SocioNegocio = SocioNegocio(**socio)
    db_session.add(socio_random)
    db_session.commit()
    logger.info('Socio creado: ' + socio_random.email)

    info_deporte = {
        'nombre': 'Atletismo',
    }
    deporte_random = Deporte(**info_deporte)
    db_session.add(deporte_random)
    db_session.commit()

    yield {
        'socio': socio_random,
        'deportes': deporte_random,
    }

    logger.info("Fin Test Agregar Productos y Servicios")
    db_session.delete(deporte_random)
    db_session.delete(socio_random)
    db_session.commit()


@pytest.mark.usefixtures("setup_data")
class TestProductosServicios():

    @patch('requests.post')
    def test_agregar_productos_servicios(self, mock_post, setup_data):
        with app.test_client() as test_client:
            socio = setup_data['socio']

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'token_valido': True, 
                'email': socio.email,
                'tipo_usuario': 'socio_negocio'
                }
            mock_post.return_value = mock_response

            headers = {'Authorization': 'Bearer 123'}

            data = {
                "email": socio.email,
                "deporte": 'Atletismo',
                "tipo": fake.random_element(elements=('producto', 'servicio')),
                "descripcion": fake.text(),
		        "subtipo": fake.word(),
                "pais": fake.country(),
                "ciudad": fake.city(),
                "lugar_entrega_prestacion": fake.city(),
                "cantidad_disponible": fake.random_int(min=2, max=10),
                "fecha_entrega_prestacion": "2024-05-01T12:00:0",
                "valor": fake.random_int(min=10000, max=1000000)
            }
            response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar', headers=headers, json=data, follow_redirects=True)
            assert response.status_code == 200

    @patch('requests.post')
    def test_listar_productos_servicios(self, mock_post, setup_data):
        with app.test_client() as test_client:
            socio = setup_data['socio']

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'token_valido': True, 
                'email': socio.email,
                'tipo_usuario': 'socio_negocio'
                }
            mock_post.return_value = mock_response

            headers = {'Authorization': 'Bearer 123'}

            response = test_client.get('/gestor-productos-servicios/productos-servicios/listar', headers=headers, follow_redirects=True)
            print ("la respuesta es: " + str(response))

            assert response.status_code == 200


    @patch('requests.post')
    def test_agregar_seccion_personalizada(self, mock_post, setup_data):
        with app.test_client() as test_client:
            socio = setup_data['socio']

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'token_valido': True, 
                'email': socio.email,
                'tipo_usuario': 'socio_negocio'
                }
            mock_post.return_value = mock_response

            headers = {'Authorization': 'Bearer 123'}

            tmp_socio = db_session.query(SocioNegocio).filter(SocioNegocio.email == setup_data['socio'].email).first()
            tmp_servicioproducto = db_session.query(ServicioProducto).filter(ServicioProducto.id_socio_negocio == tmp_socio.id).first()

            data = {
                "id_servicio_producto": tmp_servicioproducto.id,
		        "nombre_sesion": fake.word(),
                "ejercicios": [
                    {
                    "nombre": fake.word(),
                    "descripcion": fake.text(),
                    "cantidad_repeticiones":fake.random_int(min=2, max=10),
                    "duracion": fake.random_int(min=10, max=60)
                    }
                ]
            }        

            response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar-sesion-personalizada', headers=headers, json=data, follow_redirects=True)
            assert response.status_code == 200

            dele = delete(ServicioProducto).where(ServicioProducto.id_socio_negocio == socio.id)
            db_session.execute(dele)
            db_session.commit()