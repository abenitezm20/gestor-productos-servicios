# SportApp

## Gestor Productos Servicios

Aplicación encargada de realizar la gestion de productos y servicios para un socio

## Estructura del proyecto

La aplicación está construida con Python y [Flask](https://flask.palletsprojects.com/en/3.0.x/). Para el manejo de dependencias se usa [pipenv](https://pipenv-es.readthedocs.io/es/latest/).

En general dentro de cada aplicación hay dos carpetas principales, src y tests, Así como algunas rutas adicionales y varios archivos de soporte como se indican a continuación:

- **./db:** Docker Compose para crear instancia de PostgreSQL y ejecutar la aplicación de forma local

- **./k8s:** Configuración necesaria del proyecto para su despliegue en Kubernetes

- **./src:** Esta carpeta tiene el código y la lógica necesaria para exponer las funcionalidades agrupadas de este microservicio. Dentro de esta ruta se puede encontrar:

  - **./src/blueprints:** Agrupación de operaciones que se registran en la aplicación Flask para atender peticiones.

  - **./src/commands:** Esta carpeta contiene la lógica de negocio que implementa los flujos necesarios para operar SportApp. Cada operación que se implemente hereda de la clase BaseCommand para modularizar la aplicación y gestionar las peticiones recibidas en los blueprints siguiendo el patrón [Command Pattern](https://en.wikipedia.org/wiki/Command_pattern).

  - **./src/errors:** Conjunto de errores utilizados por la aplicación.

  - **./src/models:** Dentro de esta ruta se encuentra la capa de persistencia. Aquí se declara la configuración y los modelos que se gestionan en la base de datos en forma de tablas. Cada modelo hereda de la clase Model que contiene un identificador único (UUID) y la fecha de creación y modificación.

  - **./src/utils:** Utilidades transversales a la aplicación

- **./tests:** Carpeta que contiene las pruebas unitarias de los comandos implementados en la aplicación. Las pruebas unitarias necesitan de la conexión a BD y la cobertura es del 70%.

- **.env.example:** Archivo con la estructura básica para cargar variables de ambiente necesarias para la ejecución de la aplicación

- **.gitignore:** Lista de archivos y rutas que se ignoran para subir únicamente el código fuente a los repositorios GIT. Este archivo fue elaborado mediante el uso de la herramienta [gitignore.io](https://www.toptal.com/developers/gitignore)

- **Dockerfile:** Documento que contiene las instrucciones necesarias para construir la imagen de la aplicación

- **Pipfile:** Configuración del proyecto y del ambiente en el que se ejecuta la aplicación Python

## Iniciar la aplicación

Para ejecutar la aplicación localmente primero se debe configurar el archivo .env con los valores adecuados a utilizar en las variables de ambiente. En el repositorio se encuentra el archivo .env.example el cual tiene la estructura básica con la información que debe configurar para que la aplicación pueda subir de forma correcta, solo es necesario copiar el archivo y cambiar el nombre y extensión a .env y posteriormente configurar los valores apropiados al ambiente de ejecución.

Antes de ejecutar cualquier aplicación Python del sistema SportApp se debe tener una única instancia de la base de datos. Todos los proyectos cuentan con una carpeta db la cual tiene el Docker Compose ejemplo para crear una instancia de PostgreSQL.

Si no cuenta con la base de datos creada puede ejecutar desde la ruta ./db el siguiente comando:

- `docker-compose up -d`

Una vez se tengan configuradas las variables de ambiente y la base de datos este arriba, puede subir de forma local la aplicación de las siguientes maneras:

### Flask

Ejecutar los siguientes comandos desde la ruta del proyecto a nivel del archivo Pipfile:

1. `pipenv shell`
2. `pipenv install`
3. `FLASK_APP=./src/main.py flask run -h 0.0.0.0 -p 3006`

Si requiere iniciar la aplicación para desarrollar nuevas funcionalidades o corregir defectos y desea que cada modificación se carque automáticamente puede agregar la opción reload:

- `FLASK_APP=./src/main.py flask run -h 0.0.0.0 -p 3006 --reload`

### Docker

El proyecto cuenta con el archivo Dockerfile con toda la configuración necesaria para ejecutar la aplicación a través de [gunicorn](https://flask.palletsprojects.com/en/3.0.x/deploying/gunicorn/). Para crear la imagen y correr la aplicación mediante un contenedor debe ejecutar los siguientes comandos en el orden establecido:

1. `docker build . -t sport-app-gestor-productos-servicios`
2. `docker run -p 3006:3006 --name gestor-productos-servicios --env-file .env sport-app-gestor-productos-servicios`

## Pruebas unitarias

Las pruebas unitarias se realizan a través de la herramienta [pytest](https://docs.pytest.org/en/8.0.x/). El proyecto cuenta con el archivo pytest.ini con la configuración del log para la ejecución de pruebas.

Para correr las pruebas unitarias es necesario tener configuradas las variables de ambiente en el archivo .env como se indica en la sección [Iniciar la aplicación](#iniciar-la-aplicación). Puede ejecutar las pruebas unitarias ejecutando los siguientes comandos:

1. `pipenv shell`
2. `pipenv install --dev`
3. `pytest --cov-fail-under=80 --cov=src --cov-report=html`

Una vez se ejecute el ultimo comando, se corren todas las pruebas unitarias y se elabora el reporte de cobertura que puede visualizar en un navegador  abriendo el archivo ./htmlcov/index.html