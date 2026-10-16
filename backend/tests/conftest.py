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
    # check_same_thread=False porque FastAPI atiende las peticiones en otros hilos
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def activar_llaves_foraneas(conexion, _):
        # SQLite no aplica ON DELETE CASCADE si no se activa esto
        conexion.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    sesion = sessionmaker(bind=engine, autoflush=False)()
    yield sesion
    sesion.close()
    engine.dispose()


@pytest.fixture
def cliente(sesion):
    # Cliente de prueba de la API usando la base SQLite en memoria.
    # No se usa "with TestClient(...)" para que no intente conectarse a PostgreSQL al arrancar.
    from fastapi.testclient import TestClient

    from app.database import obtener_sesion
    from app.main import app
    from app.servicios.red_social import red

    app.dependency_overrides[obtener_sesion] = lambda: sesion
    red.cargar(sesion)
    yield TestClient(app)
    app.dependency_overrides.clear()
