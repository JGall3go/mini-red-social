"""Lista simplemente enlazada.

Se usa para guardar las publicaciones de cada usuario (la más nueva va de
primera) y los amigos de cada usuario dentro del grafo.

Complejidad:
    insertar_inicio  O(1)
    insertar_final   O(1)  (guardamos referencia al último nodo)
    buscar           O(n)
    eliminar         O(n)
    recorrer         O(n)
    len              O(1)
"""

from app.estructuras.nodo import Nodo


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None  # primer nodo
        self.cola = None  # último nodo
        self._tamano = 0

    def insertar_inicio(self, valor):
        # El nuevo nodo apunta a la cabeza actual y pasa a ser la cabeza. O(1)
        nuevo = Nodo(valor, self.cabeza)
        self.cabeza = nuevo
        if self.cola is None:
            self.cola = nuevo
        self._tamano += 1

    def insertar_final(self, valor):
        # Como tenemos la cola no hay que recorrer la lista. O(1)
        nuevo = Nodo(valor)
        if self.cola is None:
            self.cabeza = nuevo
        else:
            self.cola.siguiente = nuevo
        self.cola = nuevo
        self._tamano += 1

    def buscar_por(self, condicion):
        # Devuelve el primer valor que cumple la condición, o None. O(n)
        # Ejemplo: lista.buscar_por(lambda p: p.id == 7)
        actual = self.cabeza
        while actual is not None:
            if condicion(actual.valor):
                return actual.valor
            actual = actual.siguiente
        return None

    def contiene(self, valor):
        # O(n)
        return self.buscar_por(lambda v: v == valor) is not None

    def eliminar_por(self, condicion):
        # Quita el primer valor que cumple la condición y lo devuelve. O(n)
        # Para quitarlo, el nodo anterior pasa a apuntar al siguiente.
        anterior = None
        actual = self.cabeza
        while actual is not None:
            if condicion(actual.valor):
                if anterior is None:
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                if actual is self.cola:
                    self.cola = anterior
                self._tamano -= 1
                return actual.valor
            anterior = actual
            actual = actual.siguiente
        return None

    def eliminar(self, valor):
        # Devuelve True si encontró y eliminó el valor. O(n)
        return self.eliminar_por(lambda v: v == valor) is not None

    def __iter__(self):
        # Permite hacer: for valor in lista. O(n)
        actual = self.cabeza
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self._tamano == 0

    def __repr__(self):
        valores = " -> ".join(repr(v) for v in self)
        return f"ListaEnlazada({valores} -> None)" if valores else "ListaEnlazada(vacía)"
