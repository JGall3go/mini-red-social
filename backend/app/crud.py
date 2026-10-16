"""Operaciones CRUD y transacciones sobre la base de datos.

Todas las funciones reciben una sesión de SQLAlchemy. Las que cambian
datos hacen commit al final; si algo falla hacen rollback, así no queda
nada a medias.
"""

from datetime import datetime, timezone

from sqlalchemy import select, update

from app.modelos import Amistad, Like, Publicacion, SolicitudAmistad, Usuario


def _ahora():
    return datetime.now(timezone.utc)


def _guardar(sesion, objeto):
    # Guarda un objeto nuevo o modificado y lo devuelve actualizado
    try:
        sesion.add(objeto)
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    sesion.refresh(objeto)
    return objeto


# ----------------------------------------------------------------------
# Usuarios
# ----------------------------------------------------------------------
def crear_usuario(sesion, nombre_usuario, nombre_visible, biografia=None):
    usuario = Usuario(nombre_usuario=nombre_usuario.lower(), nombre_visible=nombre_visible, biografia=biografia)
    return _guardar(sesion, usuario)


def obtener_usuario(sesion, usuario_id):
    return sesion.get(Usuario, usuario_id)


def listar_usuarios(sesion):
    return sesion.scalars(select(Usuario).order_by(Usuario.id)).all()


def actualizar_usuario(sesion, usuario_id, nombre_visible=None, biografia=None):
    usuario = obtener_usuario(sesion, usuario_id)
    if usuario is None:
        return None
    if nombre_visible is not None:
        usuario.nombre_visible = nombre_visible
    if biografia is not None:
        usuario.biografia = biografia
    return _guardar(sesion, usuario)


def eliminar_usuario(sesion, usuario_id):
    # TRANSACCIÓN: antes de borrar al usuario se descuentan sus likes de las
    # publicaciones de otros. Luego la base borra en cascada sus solicitudes,
    # amistades, publicaciones y likes.
    usuario = obtener_usuario(sesion, usuario_id)
    if usuario is None:
        return False
    try:
        likes = sesion.scalars(select(Like).where(Like.usuario_id == usuario_id)).all()
        for like in likes:
            sesion.execute(
                update(Publicacion)
                .where(Publicacion.id == like.publicacion_id)
                .values(total_likes=Publicacion.total_likes - 1)
            )
        sesion.delete(usuario)
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    return True


# ----------------------------------------------------------------------
# Solicitudes de amistad y amistades
# ----------------------------------------------------------------------
def _par_ordenado(a, b):
    return (a, b) if a < b else (b, a)


def son_amigos(sesion, a, b):
    menor, mayor = _par_ordenado(a, b)
    consulta = select(Amistad).where(Amistad.usuario_a_id == menor, Amistad.usuario_b_id == mayor)
    return sesion.scalars(consulta).first() is not None


def enviar_solicitud(sesion, emisor_id, receptor_id):
    if emisor_id == receptor_id:
        raise ValueError("No puedes enviarte una solicitud a ti mismo")
    if obtener_usuario(sesion, emisor_id) is None or obtener_usuario(sesion, receptor_id) is None:
        raise ValueError("El usuario no existe")
    if son_amigos(sesion, emisor_id, receptor_id):
        raise ValueError("Ya son amigos")
    # Revisa que no haya una solicitud pendiente en ninguna de las dos direcciones
    pendiente = sesion.scalars(
        select(SolicitudAmistad).where(
            SolicitudAmistad.estado == "pendiente",
            ((SolicitudAmistad.emisor_id == emisor_id) & (SolicitudAmistad.receptor_id == receptor_id))
            | ((SolicitudAmistad.emisor_id == receptor_id) & (SolicitudAmistad.receptor_id == emisor_id)),
        )
    ).first()
    if pendiente is not None:
        raise ValueError("Ya hay una solicitud pendiente entre estos usuarios")
    return _guardar(sesion, SolicitudAmistad(emisor_id=emisor_id, receptor_id=receptor_id))


def listar_solicitudes_pendientes(sesion):
    # Todas las pendientes, de la más antigua a la más nueva (orden de la Cola)
    consulta = (
        select(SolicitudAmistad)
        .where(SolicitudAmistad.estado == "pendiente")
        .order_by(SolicitudAmistad.creada_en, SolicitudAmistad.id)
    )
    return sesion.scalars(consulta).all()


def aceptar_solicitud(sesion, solicitud_id):
    # TRANSACCIÓN: se marca la solicitud como aceptada y se crea la amistad.
    # Si falla cualquiera de los dos pasos, no se guarda ninguno.
    solicitud = sesion.get(SolicitudAmistad, solicitud_id)
    if solicitud is None or solicitud.estado != "pendiente":
        raise ValueError("La solicitud no existe o ya fue respondida")
    try:
        solicitud.estado = "aceptada"
        solicitud.respondida_en = _ahora()
        menor, mayor = _par_ordenado(solicitud.emisor_id, solicitud.receptor_id)
        amistad = Amistad(usuario_a_id=menor, usuario_b_id=mayor)
        sesion.add(amistad)
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    sesion.refresh(amistad)
    return amistad


def rechazar_solicitud(sesion, solicitud_id):
    solicitud = sesion.get(SolicitudAmistad, solicitud_id)
    if solicitud is None or solicitud.estado != "pendiente":
        raise ValueError("La solicitud no existe o ya fue respondida")
    solicitud.estado = "rechazada"
    solicitud.respondida_en = _ahora()
    return _guardar(sesion, solicitud)


def listar_amistades(sesion):
    return sesion.scalars(select(Amistad).order_by(Amistad.id)).all()


# ----------------------------------------------------------------------
# Publicaciones y likes
# ----------------------------------------------------------------------
def crear_publicacion(sesion, autor_id, contenido):
    if obtener_usuario(sesion, autor_id) is None:
        raise ValueError("El usuario no existe")
    return _guardar(sesion, Publicacion(autor_id=autor_id, contenido=contenido))


def obtener_publicacion(sesion, publicacion_id):
    return sesion.get(Publicacion, publicacion_id)


def listar_publicaciones(sesion):
    # De la más vieja a la más nueva: así, al insertarlas al inicio de la
    # lista enlazada, la más nueva queda de primera.
    consulta = select(Publicacion).order_by(Publicacion.creada_en, Publicacion.id)
    return sesion.scalars(consulta).all()


def actualizar_publicacion(sesion, publicacion_id, contenido):
    publicacion = obtener_publicacion(sesion, publicacion_id)
    if publicacion is None:
        return None
    publicacion.contenido = contenido
    return _guardar(sesion, publicacion)


def eliminar_publicacion(sesion, publicacion_id):
    publicacion = obtener_publicacion(sesion, publicacion_id)
    if publicacion is None:
        return False
    sesion.delete(publicacion)
    sesion.commit()
    return True


def dar_like(sesion, usuario_id, publicacion_id):
    # TRANSACCIÓN: se guarda el like y se suma 1 al contador del post.
    publicacion = obtener_publicacion(sesion, publicacion_id)
    if publicacion is None:
        raise ValueError("La publicación no existe")
    if sesion.get(Like, (usuario_id, publicacion_id)) is not None:
        raise ValueError("Ya le diste like a esta publicación")
    try:
        sesion.add(Like(usuario_id=usuario_id, publicacion_id=publicacion_id))
        publicacion.total_likes += 1
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    sesion.refresh(publicacion)
    return publicacion


def quitar_like(sesion, usuario_id, publicacion_id):
    # TRANSACCIÓN: se borra el like y se resta 1 al contador del post.
    like = sesion.get(Like, (usuario_id, publicacion_id))
    if like is None:
        raise ValueError("No le habías dado like a esta publicación")
    publicacion = obtener_publicacion(sesion, publicacion_id)
    try:
        sesion.delete(like)
        publicacion.total_likes -= 1
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    sesion.refresh(publicacion)
    return publicacion
