from typing import Literal

from fastapi import APIRouter, Depends

from app.database import obtener_sesion
from app.esquemas import LikeCrear, PublicacionActualizar, PublicacionCrear
from app.servicios.red_social import red

router = APIRouter(tags=["Publicaciones"])


@router.post("/publicaciones", status_code=201)
def crear_publicacion(datos: PublicacionCrear, sesion=Depends(obtener_sesion)):
    return red.crear_publicacion(sesion, datos.autor_id, datos.contenido)


@router.get("/usuarios/{usuario_id}/publicaciones")
def publicaciones_de(usuario_id: int):
    return red.publicaciones_de(usuario_id)


@router.put("/publicaciones/{publicacion_id}")
def actualizar_publicacion(publicacion_id: int, datos: PublicacionActualizar, sesion=Depends(obtener_sesion)):
    return red.actualizar_publicacion(sesion, publicacion_id, datos.contenido)


@router.delete("/publicaciones/{publicacion_id}", status_code=204)
def eliminar_publicacion(publicacion_id: int, sesion=Depends(obtener_sesion)):
    red.eliminar_publicacion(sesion, publicacion_id)


@router.post("/publicaciones/{publicacion_id}/like")
def dar_like(publicacion_id: int, datos: LikeCrear, sesion=Depends(obtener_sesion)):
    return red.cambiar_like(sesion, datos.usuario_id, publicacion_id, dar=True)


@router.delete("/publicaciones/{publicacion_id}/like")
def quitar_like(publicacion_id: int, usuario_id: int, sesion=Depends(obtener_sesion)):
    return red.cambiar_like(sesion, usuario_id, publicacion_id, dar=False)


@router.get("/usuarios/{usuario_id}/likes")
def likes_de_usuario(usuario_id: int):
    return red.likes_de(usuario_id)


@router.get("/usuarios/{usuario_id}/feed")
def feed(usuario_id: int, orden: Literal["fecha", "likes"] = "fecha"):
    return red.feed(usuario_id, orden)
