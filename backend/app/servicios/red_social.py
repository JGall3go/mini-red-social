"""Lógica de la red social usando nuestras estructuras de datos.

Al iniciar, el servidor lee la base de datos y llena las estructuras:
    - Trie: nombres de usuario (autocompletado)
    - Grafo: amistades (sugerencias y grados de separación)
    - Cola por usuario: solicitudes de amistad pendientes (FIFO)
    - Lista enlazada por usuario: sus publicaciones (la más nueva primero)
    - BST: todas las publicaciones ordenadas por likes

Cada operación que cambia datos primero se guarda en la base de datos
(crud) y, si salió bien, se actualizan las estructuras en memoria.
"""

from app import crud
from app.estructuras.bst import BST
from app.estructuras.cola import Cola
from app.estructuras.grafo import Grafo
from app.estructuras.lista_enlazada import ListaEnlazada
from app.estructuras.trie import Trie


class NoEncontrado(Exception):
    pass


def _usuario_a_dict(usuario):
    return {
        "id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario,
        "nombre_visible": usuario.nombre_visible,
        "biografia": usuario.biografia,
    }


def _publicacion_a_dict(publicacion):
    return {
        "id": publicacion.id,
        "autor_id": publicacion.autor_id,
        "contenido": publicacion.contenido,
        "total_likes": publicacion.total_likes,
        "creada_en": publicacion.creada_en.isoformat(),
    }


def _solicitud_a_dict(solicitud):
    return {
        "id": solicitud.id,
        "emisor_id": solicitud.emisor_id,
        "receptor_id": solicitud.receptor_id,
        "creada_en": solicitud.creada_en.isoformat(),
    }


def _clave_bst(post):
    # (likes, fecha, id) para que no haya claves repetidas
    return (post["total_likes"], post["creada_en"], post["id"])


def mezclar_por_fecha(lista_a, lista_b):
    # Une dos listas enlazadas ordenadas de la más nueva a la más vieja en una
    # nueva lista también ordenada (como el paso de "mezcla" del merge sort).
    resultado = ListaEnlazada()
    a = lista_a.cabeza
    b = lista_b.cabeza
    while a is not None and b is not None:
        if (a.valor["creada_en"], a.valor["id"]) >= (b.valor["creada_en"], b.valor["id"]):
            resultado.insertar_final(a.valor)
            a = a.siguiente
        else:
            resultado.insertar_final(b.valor)
            b = b.siguiente
    while a is not None:
        resultado.insertar_final(a.valor)
        a = a.siguiente
    while b is not None:
        resultado.insertar_final(b.valor)
        b = b.siguiente
    return resultado


class RedSocial:
    def __init__(self):
        self.usuarios = {}  # id -> datos del usuario
        self.ids_por_nombre = {}  # nombre_usuario -> id
        self.trie = Trie()
        self.grafo = Grafo()
        self.solicitudes = {}  # id del receptor -> Cola de solicitudes
        self.publicaciones = {}  # id del autor -> ListaEnlazada de posts
        self.ranking = BST()  # todos los posts ordenados por likes

    # ------------------------------------------------------------------
    # Carga inicial
    # ------------------------------------------------------------------
    def cargar(self, sesion):
        # Vacía todo y lo vuelve a llenar desde la base de datos
        self.__init__()
        for usuario in crud.listar_usuarios(sesion):
            self._agregar_usuario(_usuario_a_dict(usuario))
        for amistad in crud.listar_amistades(sesion):
            self.grafo.agregar_arista(amistad.usuario_a_id, amistad.usuario_b_id)
        for solicitud in crud.listar_solicitudes_pendientes(sesion):
            self.solicitudes[solicitud.receptor_id].encolar(_solicitud_a_dict(solicitud))
        for publicacion in crud.listar_publicaciones(sesion):
            self._agregar_publicacion(_publicacion_a_dict(publicacion))

    def _agregar_usuario(self, usuario):
        self.usuarios[usuario["id"]] = usuario
        self.ids_por_nombre[usuario["nombre_usuario"]] = usuario["id"]
        self.trie.insertar(usuario["nombre_usuario"])
        self.grafo.agregar_vertice(usuario["id"])
        self.solicitudes[usuario["id"]] = Cola()
        self.publicaciones[usuario["id"]] = ListaEnlazada()

    def _agregar_publicacion(self, post):
        self.publicaciones[post["autor_id"]].insertar_inicio(post)
        self.ranking.insertar(_clave_bst(post), post)

    def _obtener_usuario(self, usuario_id):
        if usuario_id not in self.usuarios:
            raise NoEncontrado("El usuario no existe")
        return self.usuarios[usuario_id]

    def _buscar_post(self, publicacion_id):
        # Busca en la lista de cada autor. O(n) en total
        for lista in self.publicaciones.values():
            post = lista.buscar_por(lambda p: p["id"] == publicacion_id)
            if post is not None:
                return post
        raise NoEncontrado("La publicación no existe")

    # ------------------------------------------------------------------
    # Usuarios
    # ------------------------------------------------------------------
    def crear_usuario(self, sesion, datos):
        usuario = crud.crear_usuario(sesion, datos.nombre_usuario, datos.nombre_visible, datos.biografia)
        nuevo = _usuario_a_dict(usuario)
        self._agregar_usuario(nuevo)
        return nuevo

    def obtener_usuario(self, usuario_id):
        usuario = dict(self._obtener_usuario(usuario_id))
        usuario["total_amigos"] = len(self.grafo.vecinos(usuario_id))
        usuario["total_publicaciones"] = len(self.publicaciones[usuario_id])
        return usuario

    def listar_usuarios(self):
        return list(self.usuarios.values())

    def actualizar_usuario(self, sesion, usuario_id, datos):
        self._obtener_usuario(usuario_id)
        usuario = crud.actualizar_usuario(sesion, usuario_id, datos.nombre_visible, datos.biografia)
        self.usuarios[usuario_id].update(_usuario_a_dict(usuario))
        return self.usuarios[usuario_id]

    def eliminar_usuario(self, sesion, usuario_id):
        self._obtener_usuario(usuario_id)
        crud.eliminar_usuario(sesion, usuario_id)
        # Borrar un usuario afecta muchas estructuras (sus amistades,
        # solicitudes, posts y los likes que dio), así que es más simple
        # y seguro volver a cargar todo desde la base de datos.
        self.cargar(sesion)

    def buscar_usuarios(self, prefijo, limite=10):
        # Autocompletado con el Trie
        nombres = self.trie.autocompletar(prefijo, limite)
        return [self.usuarios[self.ids_por_nombre[nombre]] for nombre in nombres]

    # ------------------------------------------------------------------
    # Amistades
    # ------------------------------------------------------------------
    def enviar_solicitud(self, sesion, emisor_id, receptor_id):
        self._obtener_usuario(emisor_id)
        self._obtener_usuario(receptor_id)
        solicitud = _solicitud_a_dict(crud.enviar_solicitud(sesion, emisor_id, receptor_id))
        self.solicitudes[receptor_id].encolar(solicitud)
        return solicitud

    def solicitudes_pendientes(self, usuario_id):
        # Se recorre la cola sin sacar nada, del frente al final
        self._obtener_usuario(usuario_id)
        resultado = []
        for solicitud in self.solicitudes[usuario_id]:
            item = dict(solicitud)
            item["emisor"] = self.usuarios[solicitud["emisor_id"]]
            resultado.append(item)
        return resultado

    def responder_solicitud(self, sesion, usuario_id, aceptar):
        # Siempre se responde la solicitud del frente (la más antigua)
        self._obtener_usuario(usuario_id)
        cola = self.solicitudes[usuario_id]
        if cola.esta_vacia():
            raise ValueError("No tienes solicitudes pendientes")
        solicitud = cola.ver_frente()
        if aceptar:
            crud.aceptar_solicitud(sesion, solicitud["id"])
            self.grafo.agregar_arista(solicitud["emisor_id"], solicitud["receptor_id"])
        else:
            crud.rechazar_solicitud(sesion, solicitud["id"])
        cola.desencolar()
        return solicitud

    def amigos(self, usuario_id):
        self._obtener_usuario(usuario_id)
        return [self.usuarios[i] for i in self.grafo.vecinos(usuario_id)]

    def sugerencias(self, usuario_id, limite=5):
        self._obtener_usuario(usuario_id)
        return [self.usuarios[i] for i in self.grafo.sugerencias(usuario_id, limite)]

    def grados_separacion(self, origen, destino):
        self._obtener_usuario(origen)
        self._obtener_usuario(destino)
        camino = self.grafo.grados_separacion(origen, destino)
        if camino is None:
            return {"conectados": False, "grados": None, "camino": []}
        return {
            "conectados": True,
            "grados": len(camino) - 1,
            "camino": [self.usuarios[i] for i in camino],
        }

    def datos_grafo(self):
        # Formato que usa vis-network en el frontend
        nodos = [{"id": u["id"], "label": u["nombre_usuario"]} for u in self.usuarios.values()]
        aristas = [{"from": a, "to": b} for a, b in self.grafo.aristas()]
        return {"nodos": nodos, "aristas": aristas}

    # ------------------------------------------------------------------
    # Publicaciones
    # ------------------------------------------------------------------
    def crear_publicacion(self, sesion, autor_id, contenido):
        self._obtener_usuario(autor_id)
        post = _publicacion_a_dict(crud.crear_publicacion(sesion, autor_id, contenido))
        self._agregar_publicacion(post)
        return post

    def publicaciones_de(self, usuario_id):
        self._obtener_usuario(usuario_id)
        return list(self.publicaciones[usuario_id])

    def actualizar_publicacion(self, sesion, publicacion_id, contenido):
        post = self._buscar_post(publicacion_id)
        crud.actualizar_publicacion(sesion, publicacion_id, contenido)
        # El mismo diccionario está en la lista y en el BST, así que basta
        # con cambiarlo una vez
        post["contenido"] = contenido
        return post

    def eliminar_publicacion(self, sesion, publicacion_id):
        post = self._buscar_post(publicacion_id)
        crud.eliminar_publicacion(sesion, publicacion_id)
        self.publicaciones[post["autor_id"]].eliminar_por(lambda p: p["id"] == publicacion_id)
        self.ranking.eliminar(_clave_bst(post))

    def cambiar_like(self, sesion, usuario_id, publicacion_id, dar):
        self._obtener_usuario(usuario_id)
        post = self._buscar_post(publicacion_id)
        if dar:
            actualizado = crud.dar_like(sesion, usuario_id, publicacion_id)
        else:
            actualizado = crud.quitar_like(sesion, usuario_id, publicacion_id)
        # Al cambiar los likes cambia la clave: se saca del BST y se vuelve a meter
        self.ranking.eliminar(_clave_bst(post))
        post["total_likes"] = actualizado.total_likes
        self.ranking.insertar(_clave_bst(post), post)
        return post

    def feed(self, usuario_id, orden="fecha"):
        # Publicaciones del usuario y de sus amigos
        self._obtener_usuario(usuario_id)
        autores = [usuario_id] + self.grafo.vecinos(usuario_id)
        if orden == "likes":
            # Recorrido in-order inverso del BST: más likes primero
            return [p for p in self.ranking.inorden_inverso() if p["autor_id"] in autores]
        # Por fecha: se mezclan las listas enlazadas de cada autor
        resultado = ListaEnlazada()
        for autor in autores:
            resultado = mezclar_por_fecha(resultado, self.publicaciones[autor])
        return list(resultado)

    # ------------------------------------------------------------------
    # Datos para la página de estructuras
    # ------------------------------------------------------------------
    def vista_trie(self, prefijo=""):
        # Nodos y aristas del subárbol del Trie que empieza en el prefijo.
        # El id de cada nodo es el texto que se forma hasta esa letra.
        prefijo = prefijo.lower()
        inicio = self.trie._buscar_nodo(prefijo)
        nodos, aristas = [], []
        if inicio is None:
            return {"nodos": nodos, "aristas": aristas}
        pendientes = [(inicio, prefijo)]
        while pendientes:
            nodo, texto = pendientes.pop()
            etiqueta = (texto or "*") if texto == prefijo else texto[-1]
            nodos.append({"id": texto or "*", "label": etiqueta, "es_fin": nodo.es_fin})
            for letra, hijo in nodo.hijos.items():
                aristas.append({"from": texto or "*", "to": texto + letra})
                pendientes.append((hijo, texto + letra))
        return {"nodos": nodos, "aristas": aristas}

    def vista_bst(self):
        nodos, aristas = [], []
        pendientes = [self.ranking.raiz] if self.ranking.raiz else []
        while pendientes:
            nodo = pendientes.pop()
            post = nodo.valor
            nodos.append({"id": post["id"], "label": f"#{post['id']} ({post['total_likes']} likes)"})
            for hijo, lado in ((nodo.izquierdo, "izq"), (nodo.derecho, "der")):
                if hijo is not None:
                    aristas.append({"from": post["id"], "to": hijo.valor["id"], "lado": lado})
                    pendientes.append(hijo)
        return {"nodos": nodos, "aristas": aristas, "altura": self.ranking.altura()}


# Única instancia que usa toda la API
red = RedSocial()
