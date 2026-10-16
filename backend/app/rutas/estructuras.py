"""Datos para la página que muestra cómo se ven las estructuras por dentro."""

from fastapi import APIRouter

from app.servicios.red_social import red

router = APIRouter(prefix="/estructuras", tags=["Estructuras"])


@router.get("/trie")
def ver_trie(prefijo: str = ""):
    return red.vista_trie(prefijo)


@router.get("/bst")
def ver_bst():
    return red.vista_bst()


@router.get("/cola/{usuario_id}")
def ver_cola(usuario_id: int):
    return red.solicitudes_pendientes(usuario_id)


@router.get("/lista/{usuario_id}")
def ver_lista(usuario_id: int):
    return red.publicaciones_de(usuario_id)
