from fastapi import APIRouter, Depends

from app.database import obtener_sesion
from app.esquemas import SolicitudCrear
from app.servicios.red_social import red

router = APIRouter(tags=["Amistades"])


@router.post("/solicitudes", status_code=201)
def enviar_solicitud(datos: SolicitudCrear, sesion=Depends(obtener_sesion)):
    return red.enviar_solicitud(sesion, datos.emisor_id, datos.receptor_id)


@router.get("/usuarios/{usuario_id}/solicitudes")
def solicitudes_pendientes(usuario_id: int):
    return red.solicitudes_pendientes(usuario_id)


@router.post("/usuarios/{usuario_id}/solicitudes/aceptar")
def aceptar_solicitud(usuario_id: int, sesion=Depends(obtener_sesion)):
    return red.responder_solicitud(sesion, usuario_id, aceptar=True)


@router.post("/usuarios/{usuario_id}/solicitudes/rechazar")
def rechazar_solicitud(usuario_id: int, sesion=Depends(obtener_sesion)):
    return red.responder_solicitud(sesion, usuario_id, aceptar=False)


@router.get("/usuarios/{usuario_id}/amigos")
def amigos(usuario_id: int):
    return red.amigos(usuario_id)


@router.get("/usuarios/{usuario_id}/sugerencias")
def sugerencias(usuario_id: int, limite: int = 5):
    return red.sugerencias(usuario_id, limite)


@router.get("/grados")
def grados_separacion(origen: int, destino: int):
    return red.grados_separacion(origen, destino)


@router.get("/grafo")
def grafo():
    return red.datos_grafo()
