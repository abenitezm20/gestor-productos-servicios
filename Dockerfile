# Imagen python v3.10
FROM python:3.10-alpine

# Cambia al directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios de la aplicación
COPY Pipfile Pipfile.lock /app/
COPY src /app/src

# Instala librerias necesarias para BD postgres
RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Instala pipenv y librerias necesarias de la aplicación
RUN pip install pipenv && pipenv install --system --deploy

# Variables de ambiente Flask
ENV FLASK_APP=./src/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=3006

# Variables de ambiente Gunicorn
ENV GUNICORN_NUM_WORKERS=10
ENV GUNICORN_PORT=3006

# Ejecución de la aplicación con Gunicorn
CMD ["sh", "-c", "gunicorn --workers=$GUNICORN_NUM_WORKERS --bind=0.0.0.0:$GUNICORN_PORT src.main:app"]
