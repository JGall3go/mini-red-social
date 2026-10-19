# Nodo: mini red social

Proyecto final del curso **Estructuras de Datos** (Universidad Autónoma de Occidente).

Nodo es una mini red social donde los usuarios se registran, envían y aceptan solicitudes de amistad, reciben sugerencias de amigos, ven los grados de separación entre dos personas, buscan usuarios con autocompletado, publican y dan like, y ven su red de amistades como un grafo interactivo.

El objetivo del proyecto es demostrar el uso de **5 estructuras de datos implementadas desde cero en Python**:

| Estructura | Uso en la red social |
|---|---|
| Grafo (lista de adyacencia) | Amistades, sugerencias de amigos y grados de separación (BFS) |
| Trie | Búsqueda de usuarios con autocompletado por prefijo |
| Árbol binario de búsqueda (BST) | Ordenar publicaciones por número de likes |
| Cola (con nodos) | Solicitudes de amistad pendientes en orden FIFO |
| Lista enlazada | Publicaciones de cada usuario (feed) |

## Integrante

- Juan Carlos Gallego Barona

## Enlaces del proyecto publicado

- Frontend: http://tbvtovr5u0yinbviqzzzcg7t.179.236.249.73.sslip.io/
- Backend (API): http://q2e6zcrqs6sp0tkucskzhynq.179.236.249.73.sslip.io/

## Servicios de despliegue

- **Coolify**: frontend, backend y base de datos PostgreSQL.

## Tecnologías

- Backend: Python, FastAPI, SQLAlchemy
- Base de datos: PostgreSQL
- Frontend: HTML, CSS y JavaScript puro, con vis-network para el grafo
- Pruebas: pytest

## Estructura del repositorio

```
backend/    API en FastAPI y las 5 estructuras de datos
frontend/   Interfaz web en HTML, CSS y JavaScript
docs/       Documento final
```

## Documentación

- [Documento final](docs/documento-final.md): alcance, tecnologías y explicación de cada estructura de datos.