import pytest
from sqlalchemy.exc import IntegrityError

from app import crud
from app.modelos import Amistad, Like, Publicacion, SolicitudAmistad


def crear_usuarios(sesion):
    ana = crud.crear_usuario(sesion, "ana", "Ana")
    beto = crud.crear_usuario(sesion, "beto", "Beto")
    carla = crud.crear_usuario(sesion, "carla", "Carla")
    return ana, beto, carla


# ---------------- Usuarios ----------------
def test_crud_de_usuario(sesion):
    usuario = crud.crear_usuario(sesion, "Juan", "Juan Carlos", "Hola")
    assert usuario.id is not None
    assert usuario.nombre_usuario == "juan"  # se guarda en minúscula

    crud.actualizar_usuario(sesion, usuario.id, biografia="Nueva bio")
    assert crud.obtener_usuario(sesion, usuario.id).biografia == "Nueva bio"

    assert crud.eliminar_usuario(sesion, usuario.id)
    assert crud.obtener_usuario(sesion, usuario.id) is None
    assert not crud.eliminar_usuario(sesion, usuario.id)


def test_nombre_de_usuario_repetido_falla(sesion):
    crud.crear_usuario(sesion, "ana", "Ana")
    with pytest.raises(IntegrityError):
        crud.crear_usuario(sesion, "ana", "Otra Ana")
    assert len(crud.listar_usuarios(sesion)) == 1  # el rollback dejó la sesión usable


# ---------------- Solicitudes ----------------
def test_enviar_y_aceptar_solicitud(sesion):
    ana, beto, _ = crear_usuarios(sesion)
    solicitud = crud.enviar_solicitud(sesion, ana.id, beto.id)
    assert solicitud.estado == "pendiente"

    crud.aceptar_solicitud(sesion, solicitud.id)
    assert sesion.get(SolicitudAmistad, solicitud.id).estado == "aceptada"
    assert crud.son_amigos(sesion, beto.id, ana.id)


def test_rechazar_solicitud(sesion):
    ana, beto, _ = crear_usuarios(sesion)
    solicitud = crud.enviar_solicitud(sesion, ana.id, beto.id)
    crud.rechazar_solicitud(sesion, solicitud.id)
    assert sesion.get(SolicitudAmistad, solicitud.id).estado == "rechazada"
    assert not crud.son_amigos(sesion, ana.id, beto.id)


def test_validaciones_de_solicitud(sesion):
    ana, beto, _ = crear_usuarios(sesion)
    with pytest.raises(ValueError):
        crud.enviar_solicitud(sesion, ana.id, ana.id)
    crud.enviar_solicitud(sesion, ana.id, beto.id)
    with pytest.raises(ValueError):
        crud.enviar_solicitud(sesion, beto.id, ana.id)  # ya hay una pendiente


def test_no_se_puede_responder_dos_veces(sesion):
    ana, beto, _ = crear_usuarios(sesion)
    solicitud = crud.enviar_solicitud(sesion, ana.id, beto.id)
    crud.aceptar_solicitud(sesion, solicitud.id)
    with pytest.raises(ValueError):
        crud.rechazar_solicitud(sesion, solicitud.id)


def test_pendientes_en_orden_de_llegada(sesion):
    ana, beto, carla = crear_usuarios(sesion)
    primera = crud.enviar_solicitud(sesion, ana.id, carla.id)
    segunda = crud.enviar_solicitud(sesion, beto.id, carla.id)
    ids = [s.id for s in crud.listar_solicitudes_pendientes(sesion)]
    assert ids == [primera.id, segunda.id]


def test_aceptar_hace_rollback_si_falla_la_amistad(sesion):
    # Se crea a mano una amistad que ya existe para que el INSERT falle.
    # La solicitud debe seguir "pendiente": no se guardó nada a medias.
    ana, beto, _ = crear_usuarios(sesion)
    solicitud = crud.enviar_solicitud(sesion, ana.id, beto.id)
    sesion.add(Amistad(usuario_a_id=ana.id, usuario_b_id=beto.id))
    sesion.commit()

    with pytest.raises(IntegrityError):
        crud.aceptar_solicitud(sesion, solicitud.id)
    assert sesion.get(SolicitudAmistad, solicitud.id).estado == "pendiente"
    assert len(crud.listar_amistades(sesion)) == 1


# ---------------- Publicaciones y likes ----------------
def test_crud_de_publicacion(sesion):
    ana, _, _ = crear_usuarios(sesion)
    post = crud.crear_publicacion(sesion, ana.id, "Hola mundo")
    assert post.total_likes == 0
    crud.actualizar_publicacion(sesion, post.id, "Hola Nodo")
    assert crud.obtener_publicacion(sesion, post.id).contenido == "Hola Nodo"
    assert crud.eliminar_publicacion(sesion, post.id)
    assert crud.listar_publicaciones(sesion) == []


def test_dar_y_quitar_like(sesion):
    ana, beto, _ = crear_usuarios(sesion)
    post = crud.crear_publicacion(sesion, ana.id, "Mi post")
    assert crud.dar_like(sesion, beto.id, post.id).total_likes == 1
    with pytest.raises(ValueError):
        crud.dar_like(sesion, beto.id, post.id)  # no se puede dos veces
    assert crud.quitar_like(sesion, beto.id, post.id).total_likes == 0
    assert sesion.get(Like, (beto.id, post.id)) is None


def test_eliminar_usuario_borra_en_cascada_y_ajusta_likes(sesion):
    ana, beto, _ = crear_usuarios(sesion)
    post_ana = crud.crear_publicacion(sesion, ana.id, "Post de Ana")
    crud.crear_publicacion(sesion, beto.id, "Post de Beto")
    crud.dar_like(sesion, beto.id, post_ana.id)
    solicitud = crud.enviar_solicitud(sesion, beto.id, ana.id)
    crud.aceptar_solicitud(sesion, solicitud.id)

    crud.eliminar_usuario(sesion, beto.id)
    sesion.expire_all()
    assert sesion.get(Publicacion, post_ana.id).total_likes == 0
    assert len(crud.listar_publicaciones(sesion)) == 1  # se borró el post de Beto
    assert crud.listar_amistades(sesion) == []
    assert sesion.query(SolicitudAmistad).count() == 0
