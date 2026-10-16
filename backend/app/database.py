from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

# Cada petición abre su propia sesión con SesionLocal()
SesionLocal = sessionmaker(bind=engine, autoflush=False)

# Clase base de la que heredan todos los modelos (tablas)
Base = declarative_base()
