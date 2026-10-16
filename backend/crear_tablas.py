"""Crea las tablas en la base de datos configurada en DATABASE_URL.

Uso (desde la carpeta backend): python crear_tablas.py
"""

from app import modelos  # noqa: F401  (importarlo registra las tablas)
from app.database import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tablas creadas:", ", ".join(Base.metadata.tables))
