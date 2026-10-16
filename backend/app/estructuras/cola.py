"""Cola FIFO implementada con nodos (el primero que entra es el primero que sale).

Se usa para las solicitudes de amistad pendientes de cada usuario: se
responden en el orden en que llegaron. También la usa el BFS del grafo.

Complejidad:
    encolar     O(1)
    desencolar  O(1)
    ver_frente  O(1)
    recorrer    O(n)
    len         O(1)
"""

from app.estructuras.nodo import Nodo


class Cola:
    def __init__(self):
        self.frente = None  # de aquí se saca
        self.final = None  # aquí se agrega
        self._tamano = 0

    def encolar(self, valor):
        # Se agrega al final. O(1)
        nuevo = Nodo(valor)
        if self.final is None:
            self.frente = nuevo
        else:
            self.final.siguiente = nuevo
        self.final = nuevo
        self._tamano += 1

    def desencolar(self):
        # Saca y devuelve el valor del frente. O(1)
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        valor = self.frente.valor
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self._tamano -= 1
        return valor

    def ver_frente(self):
        # Devuelve el valor del frente sin sacarlo. O(1)
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        return self.frente.valor

    def esta_vacia(self):
        return self._tamano == 0

    def __len__(self):
        return self._tamano

    def __iter__(self):
        # Recorre del frente al final sin modificar la cola. O(n)
        actual = self.frente
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def __repr__(self):
        valores = ", ".join(repr(v) for v in self)
        return f"Cola(frente -> [{valores}] <- final)"
