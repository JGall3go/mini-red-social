"""Punto de entrada de la API. Se ejecuta con: uvicorn app.main:app --reload"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import ORIGENES_PERMITIDOS
from app.database import SesionLocal
from app.rutas import amistades, estructuras, publicaciones, usuarios
from app.servicios.red_social import NoEncontrado, red


@asynccontextmanager
async def ciclo_de_vida(app):
    # Al arrancar se cargan los datos de la BD en las estructuras
    sesion = SesionLocal()
    try:
        red.cargar(sesion)
    finally:
        sesion.close()
    yield


app = FastAPI(title="Nodo - mini red social", lifespan=ciclo_de_vida)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(amistades.router)
app.include_router(publicaciones.router)
app.include_router(estructuras.router)


# Convierte nuestros errores en respuestas HTTP
@app.exception_handler(NoEncontrado)
def no_encontrado(request: Request, error: NoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(ValueError)
def dato_invalido(request: Request, error: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(error)})


@app.exception_handler(IntegrityError)
def dato_repetido(request: Request, error: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "El dato ya existe o viola una restricción"})


@app.get("/salud", tags=["Salud"])
def salud():
    return {"estado": "ok"}
