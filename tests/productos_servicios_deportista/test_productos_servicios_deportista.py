import json
import pytest
import logging
from unittest.mock import patch, MagicMock

from faker import Faker
from src.main import app
from src.models.db import db_session
from src.models.deporte import Deporte
from src.models.deportista import Deportista, TipoIdentificacionEnum, GeneroEnum
from sqlalchemy import delete

from src.models.ejercicios_sesion_personalizada import EjerciciosSesionPersonalizada
from src.models.servicio_producto import ServicioProducto
from src.models.servicio_producto_deportista import ServicioProductoDeportista
from src.models.sesion_personalizada import SesionPersonalizada
from src.models.socio_negocio import SocioNegocio, TipoIdentificacionSocioEnum

fake = Faker()
logger = logging.getLogger(__name__)

@pytest.fixture(scope="class")
def setup_data():
    with db_session() as session:
        logger.info("Inicio Test Productos y Servicios Deportista")

        # Crear Deportista
        info_deportista = {
            'nombre': fake.name(),
            'apellido': fake.name(),
            'tipo_identificacion': fake.random_element(elements=(
                tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
            'numero_identificacion': fake.random_int(min=1000000, max=999999999),
            'email': fake.email(),
            'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
            'edad': fake.random_int(min=18, max=100),
            'peso': fake.pyfloat(3, 1, positive=True),
            'altura': fake.random_int(min=140, max=200),
            'pais_nacimiento': fake.country(),
            'ciudad_nacimiento': fake.city(),
            'pais_residencia': fake.country(),
            'ciudad_residencia': fake.city(),
            'antiguedad_residencia': fake.random_int(min=0, max=10),
            'contrasena': fake.password(),
            'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
        }
        deportista_random = Deportista(**info_deportista)
        
        session.add(deportista_random)
        session.commit()
        logger.info('Deportista creado: ' + deportista_random.email)

        info_deporte = {
            'nombre': fake.name(),
        }
        deporte_random = Deporte(**info_deporte)
        session.add(deporte_random)
        session.commit()
        
        yield {
            'deportista': deportista_random,
            'deportes': deporte_random,
        }

        logger.info("Fin Test Agregar Productos y Servicios Deportista")
        session.delete(deporte_random)
        session.delete(deportista_random)
        session.commit()


@pytest.mark.usefixtures("setup_data")
class TestProductosServiciosDeportistas():

    @patch('requests.post')
    def test_comprar_productos_servicios(self, mock_post, setup_data):
        with db_session() as session:
            with app.test_client() as test_client:
                
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
                session.add(socio_random)
                session.commit()
                socio_email = socio_random.email
                socio_id= socio_random.id

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_random.email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}

                #Crear Deporte
                info_deporte = {
                    'nombre': fake.name(),
                }
                deporte_random = Deporte(**info_deporte)
                session.add(deporte_random)
                session.commit()
                deporte_nombre = deporte_random.nombre

                #Se crea el producto
                info_producto = {
                    "deporte": deporte_nombre,
                    "tipo": fake.random_element(elements=('producto', 'servicio')),
                    "descripcion": fake.word(),
                    "subtipo": fake.word(),
                    "pais": fake.country(),
                    "ciudad": fake.city(),
                    "lugar_entrega_prestacion": fake.city(),
                    "cantidad_disponible": fake.random_int(min=2, max=10),
                    "fecha_entrega_prestacion": "2024-07-01T12:00:0",
                    "valor": fake.random_int(min=10000, max=1000000)
                }
                print(info_producto)
                response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar', headers=headers, json=info_producto, follow_redirects=True)
                response_json = json.loads(response.data)
                id_producto = response_json['id_servicio_producto']

                # Crear Deportista
                info_deportista = {
                    'nombre': fake.name(),
                    'apellido': fake.name(),
                    'tipo_identificacion': fake.random_element(elements=(
                        tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
                    'numero_identificacion': fake.random_int(min=1000000, max=999999999),
                    'email': fake.email(),
                    'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
                    'edad': fake.random_int(min=18, max=100),
                    'peso': fake.pyfloat(3, 1, positive=True),
                    'altura': fake.random_int(min=140, max=200),
                    'pais_nacimiento': fake.country(),
                    'ciudad_nacimiento': fake.city(),
                    'pais_residencia': fake.country(),
                    'ciudad_residencia': fake.city(),
                    'antiguedad_residencia': fake.random_int(min=0, max=10),
                    'contrasena': fake.password(),
                    'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
                }
                deportista_random = Deportista(**info_deportista)
                session.add(deportista_random)
                session.commit()
                deportista_email = deportista_random.email

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': deportista_random.email,
                    'tipo_usuario': 'deportista'
                    }
                mock_post.return_value = mock_response
                headers = {'Authorization': 'Bearer 123'}

                #se compra el producto
                comprar_producto = {
                    "id_servicio_producto": id_producto,
                    "fecha_servicio": "2024-05-01T12:00:0",
                    "direccion_servicio": fake.city(),
                    "valor": fake.random_int(min=10000, max=1000000),
                    "telefono": fake.random_int(min=1000000, max=999999999),
                    "metodo_pago": fake.random_element(elements=('tarjeta', 'efectivo')),
                    "estado_entrega": fake.random_element(elements=('entregado', 'pendiente', 'cancelado'))
                }

                response = test_client.post('/gestor-productos-servicios/productos-servicios-deportista/comprar', headers=headers, json=comprar_producto, follow_redirects=True)
                assert response.status_code == 200

                delCompra = delete(ServicioProductoDeportista).where(ServicioProductoDeportista.id_servicio_producto == id_producto)
                session.execute(delCompra)
                session.commit()

                delServicioProducto = delete(ServicioProducto).where(ServicioProducto.id == id_producto)
                session.execute(delServicioProducto)
                session.commit()

                session.delete(deporte_random)
                session.delete(deportista_random)
                session.delete(socio_random)
                session.commit()

    @patch('requests.post')
    def test_listar_productos_servicios(self, mock_post, setup_data: Deportista):
        with db_session() as session:
            with app.test_client() as test_client:

                # Crear Deportista
                info_deportista = {
                    'nombre': fake.name(),
                    'apellido': fake.name(),
                    'tipo_identificacion': fake.random_element(elements=(
                        tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
                    'numero_identificacion': fake.random_int(min=1000000, max=999999999),
                    'email': fake.email(),
                    'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
                    'edad': fake.random_int(min=18, max=100),
                    'peso': fake.pyfloat(3, 1, positive=True),
                    'altura': fake.random_int(min=140, max=200),
                    'pais_nacimiento': fake.country(),
                    'ciudad_nacimiento': fake.city(),
                    'pais_residencia': fake.country(),
                    'ciudad_residencia': fake.city(),
                    'antiguedad_residencia': fake.random_int(min=0, max=10),
                    'contrasena': fake.password(),
                    'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
                }
                deportista_random = Deportista(**info_deportista)
                session.add(deportista_random)
                session.commit()

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': deportista_random.email,
                    'tipo_usuario': 'deportista'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}

                response = test_client.get('/gestor-productos-servicios/productos-servicios-deportista/listar', headers=headers, follow_redirects=True)

                assert response.status_code == 200

                session.delete(deportista_random)
                session.commit()


    @patch('requests.post')
    def test_listar_productos_servicios_filtros(self, mock_post, setup_data: SocioNegocio):
        with db_session() as session:
            with app.test_client() as test_client:

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
                session.add(socio_random)
                session.commit()
                socio_email = socio_random.email
                socio_id= socio_random.id

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_random.email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}

                #Crear Deporte
                info_deporte = {
                    'nombre': fake.name(),
                }
                deporte_random = Deporte(**info_deporte)
                session.add(deporte_random)
                session.commit()
                deporte_nombre = deporte_random.nombre

                #Se crea el producto
                info_producto = {
                    "deporte": deporte_nombre,
                    "tipo": fake.random_element(elements=('producto', 'servicio')),
                    "descripcion": fake.word(),
                    "subtipo": fake.word(),
                    "pais": fake.country(),
                    "ciudad": fake.city(),
                    "lugar_entrega_prestacion": fake.city(),
                    "cantidad_disponible": fake.random_int(min=2, max=10),
                    "fecha_entrega_prestacion": "2024-05-01T12:00:0",
                    "valor": fake.random_int(min=10000, max=1000000)
                }
                print(info_producto)
                response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar', headers=headers, json=info_producto, follow_redirects=True)
                response_json = json.loads(response.data)
                id_producto = response_json['id_servicio_producto']

                # Crear Deportista
                info_deportista = {
                    'nombre': fake.name(),
                    'apellido': fake.name(),
                    'tipo_identificacion': fake.random_element(elements=(
                        tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
                    'numero_identificacion': fake.random_int(min=1000000, max=999999999),
                    'email': fake.email(),
                    'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
                    'edad': fake.random_int(min=18, max=100),
                    'peso': fake.pyfloat(3, 1, positive=True),
                    'altura': fake.random_int(min=140, max=200),
                    'pais_nacimiento': fake.country(),
                    'ciudad_nacimiento': fake.city(),
                    'pais_residencia': fake.country(),
                    'ciudad_residencia': fake.city(),
                    'antiguedad_residencia': fake.random_int(min=0, max=10),
                    'contrasena': fake.password(),
                    'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
                }
                deportista_random = Deportista(**info_deportista)
                session.add(deportista_random)
                session.commit()
                deportista_email = deportista_random.email

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': deportista_random.email,
                    'tipo_usuario': 'deportista'
                    }
                mock_post.return_value = mock_response
                headers = {'Authorization': 'Bearer 123'}

                #se compra el producto
                comprar_producto = {
                    "id_servicio_producto": id_producto,
                    "fecha_servicio": "2024-05-01T12:00:0",
                    "direccion_servicio": fake.city(),
                    "valor": fake.random_int(min=10000, max=1000000),
                    "telefono": fake.random_int(min=1000000, max=999999999),
                    "metodo_pago": fake.random_element(elements=('tarjeta', 'efectivo')),
                    "estado_entrega": fake.random_element(elements=('entregado', 'pendiente', 'cancelado'))
                }

                response = test_client.post('/gestor-productos-servicios/productos-servicios-deportista/comprar', headers=headers, json=comprar_producto, follow_redirects=True)

                #Se hace la consulta de los productos
                responseConsulta = test_client.get('/gestor-productos-servicios/productos-servicios-deportista/listar/propios', headers=headers, follow_redirects=True)
                assert responseConsulta.status_code == 200

                delCompra = delete(ServicioProductoDeportista).where(ServicioProductoDeportista.id_servicio_producto == id_producto)
                session.execute(delCompra)
                session.commit()

                delServicioProducto = delete(ServicioProducto).where(ServicioProducto.id == id_producto)
                session.execute(delServicioProducto)
                session.commit()

                session.delete(deporte_random)
                session.delete(deportista_random)
                session.delete(socio_random)
                session.commit()
    

    @patch('requests.post')
    def test_listar_productos_servicios_porID(self, mock_post, setup_data: SocioNegocio):
        with db_session() as session:
            with app.test_client() as test_client:

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
                session.add(socio_random)
                session.commit()
                socio_email = socio_random.email
                socio_id= socio_random.id

                info_deporte = {
                    'nombre': fake.name(),
                }
                deporte_random = Deporte(**info_deporte)
                session.add(deporte_random)
                session.commit()
                deporte_id = deporte_random.id

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_random.email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}

                #Se agrega un producto
                servicio_producto = {
                    "email": socio_random.email,
                    "deporte": deporte_random.nombre,
                    "tipo": fake.random_element(elements=('producto', 'servicio')),
                    "descripcion": fake.word(),
                    "subtipo": fake.word(),
                    "pais": fake.country(),
                    "ciudad": fake.city(),
                    "lugar_entrega_prestacion": fake.city(),
                    "cantidad_disponible": fake.random_int(min=2, max=10),
                    "fecha_entrega_prestacion": "2024-05-01T12:00:0",
                    "valor": fake.random_int(min=10000, max=1000000)
                }
                response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar', headers=headers, json=servicio_producto, follow_redirects=True)
                response_json = json.loads(response.data)

                # Crear Deportista
                info_deportista = {
                    'nombre': fake.name(),
                    'apellido': fake.name(),
                    'tipo_identificacion': fake.random_element(elements=(
                        tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
                    'numero_identificacion': fake.random_int(min=1000000, max=999999999),
                    'email': fake.email(),
                    'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
                    'edad': fake.random_int(min=18, max=100),
                    'peso': fake.pyfloat(3, 1, positive=True),
                    'altura': fake.random_int(min=140, max=200),
                    'pais_nacimiento': fake.country(),
                    'ciudad_nacimiento': fake.city(),
                    'pais_residencia': fake.country(),
                    'ciudad_residencia': fake.city(),
                    'antiguedad_residencia': fake.random_int(min=0, max=10),
                    'contrasena': fake.password(),
                    'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
                }
                deportista_random = Deportista(**info_deportista)
                session.add(deportista_random)
                session.commit()
                deportista_email = deportista_random.email

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': deportista_random.email,
                    'tipo_usuario': 'deportista'
                    }
                mock_post.return_value = mock_response
                headers = {'Authorization': 'Bearer 123'}

                responseConsulta = test_client.get('/gestor-productos-servicios/productos-servicios-deportista/listarID/'+response_json['id_servicio_producto'], headers=headers, follow_redirects=True)

                assert responseConsulta.status_code == 200

                delServicioProducto = delete(ServicioProducto).where(ServicioProducto.id_socio_negocio == socio_id)
                session.execute(delServicioProducto)
                session.commit()

                delDeporte = delete(Deporte).where(Deporte.id == deporte_id)
                session.execute(delDeporte)
                session.commit()

                delSocioNegocio = delete(SocioNegocio).where(SocioNegocio.id == socio_id)
                session.execute(delSocioNegocio)
                session.commit()

                session.delete(deportista_random)
                session.commit()


    @patch('requests.post')
    def test_listar_productos_servicios_caducados(self, mock_post, setup_data: SocioNegocio):
        with db_session() as session:
            with app.test_client() as test_client:

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
                session.add(socio_random)
                session.commit()
                socio_email = socio_random.email
                socio_id= socio_random.id

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_random.email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}

                #Crear Deporte
                info_deporte = {
                    'nombre': fake.name(),
                }
                deporte_random = Deporte(**info_deporte)
                session.add(deporte_random)
                session.commit()
                deporte_nombre = deporte_random.nombre

                #Se crea el producto
                info_producto = {
                    "deporte": deporte_nombre,
                    "tipo": fake.random_element(elements=('producto', 'servicio')),
                    "descripcion": fake.word(),
                    "subtipo": fake.word(),
                    "pais": fake.country(),
                    "ciudad": fake.city(),
                    "lugar_entrega_prestacion": fake.city(),
                    "cantidad_disponible": fake.random_int(min=2, max=10),
                    "fecha_entrega_prestacion": "2024-05-01T12:00:0",
                    "valor": fake.random_int(min=10000, max=1000000)
                }
                print(info_producto)
                response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar', headers=headers, json=info_producto, follow_redirects=True)
                response_json = json.loads(response.data)
                id_producto = response_json['id_servicio_producto']

                # Crear Deportista
                info_deportista = {
                    'nombre': fake.name(),
                    'apellido': fake.name(),
                    'tipo_identificacion': fake.random_element(elements=(
                        tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
                    'numero_identificacion': fake.random_int(min=1000000, max=999999999),
                    'email': fake.email(),
                    'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
                    'edad': fake.random_int(min=18, max=100),
                    'peso': fake.pyfloat(3, 1, positive=True),
                    'altura': fake.random_int(min=140, max=200),
                    'pais_nacimiento': fake.country(),
                    'ciudad_nacimiento': fake.city(),
                    'pais_residencia': fake.country(),
                    'ciudad_residencia': fake.city(),
                    'antiguedad_residencia': fake.random_int(min=0, max=10),
                    'contrasena': fake.password(),
                    'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
                }
                deportista_random = Deportista(**info_deportista)
                session.add(deportista_random)
                session.commit()
                deportista_email = deportista_random.email

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': deportista_random.email,
                    'tipo_usuario': 'deportista'
                    }
                mock_post.return_value = mock_response
                headers = {'Authorization': 'Bearer 123'}

                #se compra el producto
                comprar_producto = {
                    "id_servicio_producto": id_producto,
                    "fecha_servicio": "2024-05-01T12:00:0",
                    "direccion_servicio": fake.city(),
                    "valor": fake.random_int(min=10000, max=1000000),
                    "telefono": fake.random_int(min=1000000, max=999999999),
                    "metodo_pago": fake.random_element(elements=('tarjeta', 'efectivo')),
                    "estado_entrega": fake.random_element(elements=('entregado', 'pendiente', 'cancelado'))
                }

                response = test_client.post('/gestor-productos-servicios/productos-servicios-deportista/comprar', headers=headers, json=comprar_producto, follow_redirects=True)

                #Se hace la consulta de los productos
                responseConsulta = test_client.get('/gestor-productos-servicios/productos-servicios-deportista/listar', headers=headers, follow_redirects=True)
                response_json = json.loads(responseConsulta.data)

                assert responseConsulta.status_code == 200

                delCompra = delete(ServicioProductoDeportista).where(ServicioProductoDeportista.id_servicio_producto == id_producto)
                session.execute(delCompra)
                session.commit()

                delServicioProducto = delete(ServicioProducto).where(ServicioProducto.id == id_producto)
                session.execute(delServicioProducto)
                session.commit()

                session.delete(deporte_random)
                session.delete(deportista_random)
                session.delete(socio_random)
                session.commit()


    @patch('requests.post')
    def test_listar_compradores(self, mock_post, setup_data: SocioNegocio):
        with db_session() as session:
            with app.test_client() as test_client:

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
                session.add(socio_random)
                session.commit()
                socio_email = socio_random.email
                socio_id= socio_random.id

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_random.email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}

                #Crear Deporte
                info_deporte = {
                    'nombre': fake.name(),
                }
                deporte_random = Deporte(**info_deporte)
                session.add(deporte_random)
                session.commit()
                deporte_nombre = deporte_random.nombre

                #Se crea el producto
                info_producto = {
                    "deporte": deporte_nombre,
                    "tipo": fake.random_element(elements=('producto', 'servicio')),
                    "descripcion": fake.word(),
                    "subtipo": fake.word(),
                    "pais": fake.country(),
                    "ciudad": fake.city(),
                    "lugar_entrega_prestacion": fake.city(),
                    "cantidad_disponible": fake.random_int(min=2, max=10),
                    "fecha_entrega_prestacion": "2024-05-01T12:00:0",
                    "valor": fake.random_int(min=10000, max=1000000)
                }
                #print(info_producto)
                response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar', headers=headers, json=info_producto, follow_redirects=True)
                response_json = json.loads(response.data)
                id_producto = response_json['id_servicio_producto']

                # Crear Deportista
                info_deportista = {
                    'nombre': fake.name(),
                    'apellido': fake.name(),
                    'tipo_identificacion': fake.random_element(elements=(
                        tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
                    'numero_identificacion': fake.random_int(min=1000000, max=999999999),
                    'email': fake.email(),
                    'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
                    'edad': fake.random_int(min=18, max=100),
                    'peso': fake.pyfloat(3, 1, positive=True),
                    'altura': fake.random_int(min=140, max=200),
                    'pais_nacimiento': fake.country(),
                    'ciudad_nacimiento': fake.city(),
                    'pais_residencia': fake.country(),
                    'ciudad_residencia': fake.city(),
                    'antiguedad_residencia': fake.random_int(min=0, max=10),
                    'contrasena': fake.password(),
                    'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
                }
                deportista_random = Deportista(**info_deportista)
                session.add(deportista_random)
                session.commit()
                deportista_email = deportista_random.email

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': deportista_random.email,
                    'tipo_usuario': 'deportista'
                    }
                mock_post.return_value = mock_response
                headers = {'Authorization': 'Bearer 123'}

                #se compra el producto
                comprar_producto = {
                    "id_servicio_producto": id_producto,
                    "fecha_servicio": "2024-05-01T12:00:0",
                    "direccion_servicio": fake.city(),
                    "valor": fake.random_int(min=10000, max=1000000),
                    "telefono": fake.random_int(min=1000000, max=999999999),
                    "metodo_pago": fake.random_element(elements=('tarjeta', 'efectivo')),
                    "estado_entrega": fake.random_element(elements=('entregado', 'pendiente', 'cancelado'))
                }

                response = test_client.post('/gestor-productos-servicios/productos-servicios-deportista/comprar', headers=headers, json=comprar_producto, follow_redirects=True)

                #Se hace la consulta de los productos que han comprado
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}
                responseConsulta = test_client.get('/gestor-productos-servicios/productos-servicios/listar-compradores/'+id_producto, headers=headers, follow_redirects=True)
                assert responseConsulta.status_code == 200

                delCompra = delete(ServicioProductoDeportista).where(ServicioProductoDeportista.id_servicio_producto == id_producto)
                session.execute(delCompra)
                session.commit()

                delServicioProducto = delete(ServicioProducto).where(ServicioProducto.id == id_producto)
                session.execute(delServicioProducto)
                session.commit()

                session.delete(deporte_random)
                session.delete(deportista_random)
                session.delete(socio_random)
                session.commit()


    @patch('requests.post')
    def test_listar_sesion_personalizada_deportista(self, mock_post, setup_data: SocioNegocio):
        with db_session() as session:
            with app.test_client() as test_client:

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
                session.add(socio_random)
                session.commit()
                socio_email = socio_random.email
                socio_id= socio_random.id

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_random.email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}

                #Crear Deporte
                info_deporte = {
                    'nombre': fake.name(),
                }
                deporte_random = Deporte(**info_deporte)
                session.add(deporte_random)
                session.commit()
                deporte_nombre = deporte_random.nombre

                #Se crea el producto
                info_producto = {
                    "deporte": deporte_nombre,
                    "tipo": fake.random_element(elements=('producto', 'servicio')),
                    "descripcion": fake.word(),
                    "subtipo": fake.word(),
                    "pais": fake.country(),
                    "ciudad": fake.city(),
                    "lugar_entrega_prestacion": fake.city(),
                    "cantidad_disponible": fake.random_int(min=2, max=10),
                    "fecha_entrega_prestacion": "2024-05-01T12:00:0",
                    "valor": fake.random_int(min=10000, max=1000000)
                }
                #print(info_producto)
                response = test_client.post('/gestor-productos-servicios/productos-servicios/agregar', headers=headers, json=info_producto, follow_redirects=True)
                response_json = json.loads(response.data)
                id_producto = response_json['id_servicio_producto']

                #se almacenara la sesion personalizada
                info_sesion_personalizada = {
                    "id_servicio_producto": id_producto,
                    "nombre_sesion": fake.word(),
                    "ejercicios": [
                    {
                    "nombre": fake.word(),
                    "descripcion": fake.word(),
                    "cantidad_repeticiones":fake.random_int(min=2, max=10),
                    "duracion": fake.random_int(min=10, max=30),
                    }]
                }
                response_sesion = test_client.post('/gestor-productos-servicios/productos-servicios/agregar-sesion-personalizada', headers=headers, json=info_sesion_personalizada, follow_redirects=True)

                # Crear Deportista
                info_deportista = {
                    'nombre': fake.name(),
                    'apellido': fake.name(),
                    'tipo_identificacion': fake.random_element(elements=(
                        tipo_identificacion.value for tipo_identificacion in TipoIdentificacionEnum)),
                    'numero_identificacion': fake.random_int(min=1000000, max=999999999),
                    'email': fake.email(),
                    'genero': fake.random_element(elements=(genero.value for genero in GeneroEnum)),
                    'edad': fake.random_int(min=18, max=100),
                    'peso': fake.pyfloat(3, 1, positive=True),
                    'altura': fake.random_int(min=140, max=200),
                    'pais_nacimiento': fake.country(),
                    'ciudad_nacimiento': fake.city(),
                    'pais_residencia': fake.country(),
                    'ciudad_residencia': fake.city(),
                    'antiguedad_residencia': fake.random_int(min=0, max=10),
                    'contrasena': fake.password(),
                    'deportes' : [ {"atletismo": 1}, {"ciclismo": 0}]
                }
                deportista_random = Deportista(**info_deportista)
                session.add(deportista_random)
                session.commit()
                deportista_email = deportista_random.email

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': deportista_random.email,
                    'tipo_usuario': 'deportista'
                    }
                mock_post.return_value = mock_response
                headers = {'Authorization': 'Bearer 123'}

                #se compra el producto
                comprar_producto = {
                    "id_servicio_producto": id_producto,
                    "fecha_servicio": "2024-05-01T12:00:0",
                    "direccion_servicio": fake.city(),
                    "valor": fake.random_int(min=10000, max=1000000),
                    "telefono": fake.random_int(min=1000000, max=999999999),
                    "metodo_pago": fake.random_element(elements=('tarjeta', 'efectivo')),
                    "estado_entrega": fake.random_element(elements=('entregado', 'pendiente', 'cancelado'))
                }

                response = test_client.post('/gestor-productos-servicios/productos-servicios-deportista/comprar', headers=headers, json=comprar_producto, follow_redirects=True)

                #Se hace la consulta de los productos que han comprado
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'token_valido': True, 
                    'email': socio_email,
                    'tipo_usuario': 'socio_negocio'
                    }
                mock_post.return_value = mock_response

                headers = {'Authorization': 'Bearer 123'}
                responseConsulta = test_client.get('/gestor-productos-servicios/productos-servicios/listar-sesion-personalizada/'+id_producto, headers=headers, follow_redirects=True)
                assert responseConsulta.status_code == 200
                
                sesion_personalizada = SesionPersonalizada.query.filter(SesionPersonalizada.id_servicio_producto == id_producto).first()
                delEjercicios = delete(EjerciciosSesionPersonalizada).where(EjerciciosSesionPersonalizada.id_sesion_personalizada == sesion_personalizada.id)
                session.execute(delEjercicios)
                session.commit()

                delSesion = delete(SesionPersonalizada).where(SesionPersonalizada.id_servicio_producto == id_producto)
                session.execute(delSesion)
                session.commit()

                delCompra = delete(ServicioProductoDeportista).where(ServicioProductoDeportista.id_servicio_producto == id_producto)
                session.execute(delCompra)
                session.commit()

                delServicioProducto = delete(ServicioProducto).where(ServicioProducto.id == id_producto)
                session.execute(delServicioProducto)
                session.commit()

                session.delete(deporte_random)
                session.delete(deportista_random)
                session.delete(socio_random)
                session.commit()