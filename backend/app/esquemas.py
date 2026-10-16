"""Datos que recibe la API (validados con Pydantic)."""

from typing import Optional

from pydantic import BaseModel, Field


class UsuarioCrear(BaseModel):
    # Solo letras, números y guion bajo, entre 3 y 30 caracteres
    nombre_usuario: str = Field(pattern=r"^[A-Za-z0-9_]{3,30}$")
    nombre_visible: str = Field(min_length=1, max_length=60)
    biografia: Optional[str] = Field(default=None, max_length=200)


class UsuarioActualizar(BaseModel):
    nombre_visible: Optional[str] = Field(default=None, min_length=1, max_length=60)
    biografia: Optional[str] = Field(default=None, max_length=200)


class SolicitudCrear(BaseModel):
    emisor_id: int
    receptor_id: int


class PublicacionCrear(BaseModel):
    autor_id: int
    contenido: str = Field(min_length=1, max_length=280)


class PublicacionActualizar(BaseModel):
    contenido: str = Field(min_length=1, max_length=280)


class LikeCrear(BaseModel):
    usuario_id: int
