"""Tablas de la base de datos (modelos de SQLAlchemy)."""

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func, text

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(30), unique=True, nullable=False)
    nombre_visible = Column(String(60), nullable=False)
    biografia = Column(String(200))
    creado_en = Column(DateTime(timezone=True), server_default=func.now())


class SolicitudAmistad(Base):
    __tablename__ = "solicitudes_amistad"

    id = Column(Integer, primary_key=True)
    emisor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    receptor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    estado = Column(String(10), nullable=False, default="pendiente")
    creada_en = Column(DateTime(timezone=True), server_default=func.now())
    respondida_en = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("emisor_id <> receptor_id", name="solicitud_no_a_si_mismo"),
        CheckConstraint("estado IN ('pendiente', 'aceptada', 'rechazada')", name="solicitud_estado_valido"),
        # No puede haber dos solicitudes pendientes entre el mismo par
        Index(
            "solicitud_pendiente_unica",
            "emisor_id",
            "receptor_id",
            unique=True,
            postgresql_where=text("estado = 'pendiente'"),
            sqlite_where=text("estado = 'pendiente'"),
        ),
    )


class Amistad(Base):
    __tablename__ = "amistades"

    id = Column(Integer, primary_key=True)
    usuario_a_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    usuario_b_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    creada_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Se guarda siempre el id menor en usuario_a para no repetir la amistad
        CheckConstraint("usuario_a_id < usuario_b_id", name="amistad_orden"),
        UniqueConstraint("usuario_a_id", "usuario_b_id", name="amistad_unica"),
    )


class Publicacion(Base):
    __tablename__ = "publicaciones"

    id = Column(Integer, primary_key=True)
    autor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    contenido = Column(String(280), nullable=False)
    total_likes = Column(Integer, nullable=False, default=0)
    creada_en = Column(DateTime(timezone=True), server_default=func.now())


class Like(Base):
    __tablename__ = "likes"

    # La llave primaria compuesta evita que alguien dé like dos veces al mismo post
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    publicacion_id = Column(Integer, ForeignKey("publicaciones.id", ondelete="CASCADE"), primary_key=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
