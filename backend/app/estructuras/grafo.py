"""Grafo no dirigido con lista de adyacencia para las amistades.

Cada usuario es un vértice y cada amistad es una arista entre dos usuarios.
Se usa un diccionario {usuario: ListaEnlazada de amigos}, así cada usuario
tiene su propia lista de vecinos.

El BFS (búsqueda en anchura) recorre el grafo por niveles usando nuestra
Cola: primero los amigos, luego los amigos de los amigos, etc. Con eso
salen las sugerencias de amigos y los grados de separación.

Complejidad (V = usuarios, E = amistades, g = número de amigos):
    agregar_vertice    O(1)
    agregar_arista     O(g)  (se revisa que no estén ya conectados)
    eliminar_arista    O(g)
    eliminar_vertice   O(V + E) en el peor caso
    son_amigos         O(g)
    vecinos            O(g)
    bfs                O(V + E)
    sugerencias        O(V + E)
    grados_separacion  O(V + E)
"""

from app.estructuras.cola import Cola
from app.estructuras.lista_enlazada import ListaEnlazada


class Grafo:
    def __init__(self):
        self.adyacencia = {}  # usuario -> ListaEnlazada con sus amigos

    def agregar_vertice(self, usuario):
        # O(1)
        if usuario not in self.adyacencia:
            self.adyacencia[usuario] = ListaEnlazada()

    def eliminar_vertice(self, usuario):
        # Se quita el usuario de la lista de cada amigo y luego el usuario.
        if usuario not in self.adyacencia:
            return False
        for amigo in self.adyacencia[usuario]:
            self.adyacencia[amigo].eliminar(usuario)
        del self.adyacencia[usuario]
        return True

    def agregar_arista(self, a, b):
        # La amistad va en las dos direcciones. Devuelve False si ya existía.
        if a == b:
            raise ValueError("Un usuario no puede ser amigo de sí mismo")
        self.agregar_vertice(a)
        self.agregar_vertice(b)
        if self.son_amigos(a, b):
            return False
        self.adyacencia[a].insertar_final(b)
        self.adyacencia[b].insertar_final(a)
        return True

    def eliminar_arista(self, a, b):
        if not self.son_amigos(a, b):
            return False
        self.adyacencia[a].eliminar(b)
        self.adyacencia[b].eliminar(a)
        return True

    def son_amigos(self, a, b):
        return a in self.adyacencia and self.adyacencia[a].contiene(b)

    def vecinos(self, usuario):
        # Lista de amigos del usuario (vacía si no existe).
        if usuario not in self.adyacencia:
            return []
        return list(self.adyacencia[usuario])

    def bfs(self, origen):
        # Devuelve los usuarios en el orden en que el BFS los visita.
        if origen not in self.adyacencia:
            return []
        visitados = {origen}
        orden = []
        cola = Cola()
        cola.encolar(origen)
        while not cola.esta_vacia():
            actual = cola.desencolar()
            orden.append(actual)
            for amigo in self.adyacencia[actual]:
                if amigo not in visitados:
                    visitados.add(amigo)
                    cola.encolar(amigo)
        return orden

    def sugerencias(self, usuario, limite=5):
        # Amigos de mis amigos que todavía no son mis amigos (distancia 2).
        # Se ordenan por cantidad de amigos en común, de mayor a menor.
        if usuario not in self.adyacencia:
            return []
        en_comun = {}  # candidato -> número de amigos en común
        for amigo in self.adyacencia[usuario]:
            for candidato in self.adyacencia[amigo]:
                if candidato != usuario and not self.son_amigos(usuario, candidato):
                    en_comun[candidato] = en_comun.get(candidato, 0) + 1
        ordenados = sorted(en_comun.items(), key=lambda par: (-par[1], par[0]))
        return [candidato for candidato, _ in ordenados[:limite]]

    def grados_separacion(self, origen, destino):
        # Devuelve el camino más corto entre dos usuarios, o None si no
        # están conectados. Los grados de separación son len(camino) - 1.
        if origen not in self.adyacencia or destino not in self.adyacencia:
            return None
        padre = {origen: None}  # de qué usuario llegamos a cada uno
        cola = Cola()
        cola.encolar(origen)
        while not cola.esta_vacia():
            actual = cola.desencolar()
            if actual == destino:
                break
            for amigo in self.adyacencia[actual]:
                if amigo not in padre:
                    padre[amigo] = actual
                    cola.encolar(amigo)
        if destino not in padre:
            return None
        # Se reconstruye el camino yendo hacia atrás desde el destino.
        camino = []
        actual = destino
        while actual is not None:
            camino.append(actual)
            actual = padre[actual]
        camino.reverse()
        return camino

    def aristas(self):
        # Cada amistad una sola vez, útil para dibujar el grafo.
        resultado = []
        for usuario in self.adyacencia:
            for amigo in self.adyacencia[usuario]:
                if usuario < amigo:
                    resultado.append((usuario, amigo))
        return resultado

    def __len__(self):
        return len(self.adyacencia)
