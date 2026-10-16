"""Árbol binario de búsqueda (BST) para ordenar publicaciones por likes.

Cada nodo guarda una clave y un valor. A la izquierda van las claves
menores y a la derecha las mayores, así el recorrido in-order devuelve
todo ordenado.

Para las publicaciones la clave es (likes, fecha, id): si dos posts tienen
los mismos likes se desempata por fecha y luego por id, así no hay claves
repetidas.

Complejidad (h = altura del árbol):
    insertar  O(h)
    buscar    O(h)
    eliminar  O(h)
    inorden   O(n)
h es log n si el árbol está balanceado, pero puede llegar a n si las
claves llegan ya ordenadas (el árbol queda como una lista).
"""


class NodoBST:
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izquierdo = None
        self.derecho = None


class BST:
    def __init__(self):
        self.raiz = None
        self._tamano = 0

    def insertar(self, clave, valor):
        # Si la clave ya existe solo se actualiza el valor. O(h)
        if self.raiz is None:
            self.raiz = NodoBST(clave, valor)
            self._tamano += 1
            return
        actual = self.raiz
        while True:
            if clave == actual.clave:
                actual.valor = valor
                return
            if clave < actual.clave:
                if actual.izquierdo is None:
                    actual.izquierdo = NodoBST(clave, valor)
                    break
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = NodoBST(clave, valor)
                    break
                actual = actual.derecho
        self._tamano += 1

    def buscar(self, clave):
        # Devuelve el valor de la clave, o None si no está. O(h)
        actual = self.raiz
        while actual is not None:
            if clave == actual.clave:
                return actual.valor
            if clave < actual.clave:
                actual = actual.izquierdo
            else:
                actual = actual.derecho
        return None

    def eliminar(self, clave):
        # Devuelve True si la clave existía. O(h)
        if self.buscar(clave) is None:
            return False
        self.raiz = self._eliminar(self.raiz, clave)
        self._tamano -= 1
        return True

    def _eliminar(self, nodo, clave):
        # Devuelve la nueva raíz del subárbol después de eliminar.
        if clave < nodo.clave:
            nodo.izquierdo = self._eliminar(nodo.izquierdo, clave)
            return nodo
        if clave > nodo.clave:
            nodo.derecho = self._eliminar(nodo.derecho, clave)
            return nodo
        # Caso 1 y 2: el nodo tiene uno o ningún hijo, lo reemplaza ese hijo.
        if nodo.izquierdo is None:
            return nodo.derecho
        if nodo.derecho is None:
            return nodo.izquierdo
        # Caso 3: tiene dos hijos. Se reemplaza por el menor de la derecha
        # (su sucesor) y luego se elimina ese sucesor.
        sucesor = nodo.derecho
        while sucesor.izquierdo is not None:
            sucesor = sucesor.izquierdo
        nodo.clave = sucesor.clave
        nodo.valor = sucesor.valor
        nodo.derecho = self._eliminar(nodo.derecho, sucesor.clave)
        return nodo

    def inorden(self):
        # Valores de menor a mayor clave: izquierdo, nodo, derecho. O(n)
        resultado = []
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo, resultado):
        if nodo is not None:
            self._inorden(nodo.izquierdo, resultado)
            resultado.append(nodo.valor)
            self._inorden(nodo.derecho, resultado)

    def inorden_inverso(self):
        # Valores de mayor a menor clave (los posts con más likes primero). O(n)
        resultado = []
        self._inorden_inverso(self.raiz, resultado)
        return resultado

    def _inorden_inverso(self, nodo, resultado):
        if nodo is not None:
            self._inorden_inverso(nodo.derecho, resultado)
            resultado.append(nodo.valor)
            self._inorden_inverso(nodo.izquierdo, resultado)

    def altura(self):
        # Número de niveles del árbol (0 si está vacío). O(n)
        return self._altura(self.raiz)

    def _altura(self, nodo):
        if nodo is None:
            return 0
        return 1 + max(self._altura(nodo.izquierdo), self._altura(nodo.derecho))

    def __len__(self):
        return self._tamano

    def esta_vacio(self):
        return self._tamano == 0
