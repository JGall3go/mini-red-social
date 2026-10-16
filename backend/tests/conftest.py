import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import modelos  # noqa: F401
from app.database import Base


@pytest.fixture
def sesion():
    # Base de datos SQLite en memoria: cada prueba empieza con tablas vacías
    # y no hace falta tener PostgreSQL para correr las pruebas.
    engine = create_engine("sqlite://", poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def activar_llaves_foraneas(conexion, _):
        # SQLite no aplica ON DELETE CASCADE si no se activa esto
        conexion.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    sesion = sessionmaker(bind=engine, autoflush=False)()
    yield sesion
    sesion.close()
    engine.dispose()
