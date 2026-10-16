from fastapi import APIRouter, Depends

from app.database import obtener_sesion
from app.esquemas import UsuarioActualizar, UsuarioCrear
from app.servicios.red_social import red

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("", status_code=201)
def crear_usuario(datos: UsuarioCrear, sesion=Depends(obtener_sesion)):
    return red.crear_usuario(sesion, datos)


@router.get("")
def listar_usuarios():
    return red.listar_usuarios()


# Va antes de /{usuario_id} para que "buscar" no se tome como un id
@router.get("/buscar")
def buscar_usuarios(prefijo: str, limite: int = 10):
    return red.buscar_usuarios(prefijo, limite)


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int):
    return red.obtener_usuario(usuario_id)


@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: int, datos: UsuarioActualizar, sesion=Depends(obtener_sesion)):
    return red.actualizar_usuario(sesion, usuario_id, datos)


@router.delete("/{usuario_id}", status_code=204)
def eliminar_usuario(usuario_id: int, sesion=Depends(obtener_sesion)):
    red.eliminar_usuario(sesion, usuario_id)
