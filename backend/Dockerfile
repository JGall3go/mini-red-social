# Imagen de la API para desplegar en Coolify
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Crea las tablas si no existen y arranca la API.
# Un solo worker: las estructuras viven en memoria y con varios procesos cada uno tendría su copia.
CMD ["sh", "-c", "python crear_tablas.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
