import os

from dotenv import load_dotenv

# Lee las variables del archivo .env (si existe)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://nodo:nodo@localhost:5433/nodo")

# Coolify entrega la URL como postgres://... y SQLAlchemy necesita indicar el driver psycopg
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Direcciones desde las que el frontend puede llamar a la API, separadas por coma
ORIGENES_PERMITIDOS = os.getenv("ORIGENES_PERMITIDOS", "*").split(",")
