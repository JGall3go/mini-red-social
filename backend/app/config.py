import os

from dotenv import load_dotenv

# Lee las variables del archivo .env (si existe)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://nodo:nodo@localhost:5433/nodo")

# Direcciones desde las que el frontend puede llamar a la API, separadas por coma
ORIGENES_PERMITIDOS = os.getenv("ORIGENES_PERMITIDOS", "*").split(",")
