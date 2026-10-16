"""Lista simplemente enlazada.

Uso en Nodo:
- Las publicaciones de cada usuario (su feed). Cada publicación nueva se
  inserta al inicio, así la lista queda siempre de la más reciente a la más
  antigua sin necesidad de ordenar.
- Los vecinos (amigos) de cada usuario dentro del Grafo.

Complejidad (n = número de elementos):

    insertar_inicio   O(1)
    insertar_final    O(1)   gracias a la referencia al último nodo (cola)
    buscar            O(n)
    eliminar          O(n)
    recorrer          O(n)
    len / esta_vacia  O(1)   el tamaño se guarda en un contador
"""

from app.estructuras.nodo import Nodo


class ListaEnlazada:
    """Cadena de nodos con referencias a la cabeza (primero) y a la cola (último)."""

    def __init__(self):
        self.cabeza = None  # primer nodo, o None si la lista está vacía
        self.cola = None    # último nodo, permite insertar al final en O(1)
        self._tamano = 0

    # ------------------------------------------------------------------
    # Inserción
    # ------------------------------------------------------------------
    def insertar_inicio(self, valor):
        """Agrega un valor al principio. O(1).

        El nuevo nodo apunta a la cabeza actual y pasa a ser la nueva cabeza.
        """
        nuevo = Nodo(valor, self.cabeza)
        self.cabeza = nuevo
        if self.cola is None:  # la lista estaba vacía
            self.cola = nuevo
        self._tamano += 1

    def insertar_final(self, valor):
        """Agrega un valor al final. O(1).

        Sin la referencia `cola` habría que recorrer toda la lista para
        encontrar el último nodo, lo que costaría O(n).
        """
        nuevo = Nodo(valor)
        if self.cola is None:  # la lista estaba vacía
            self.cabeza = nuevo
        else:
            self.cola.siguiente = nuevo
        self.cola = nuevo
        self._tamano += 1

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------
    def buscar_por(self, condicion):
        """Devuelve el primer valor que cumple `condicion(valor)`, o None. O(n).

        Ejemplo: lista.buscar_por(lambda p: p.id == 7)
        """
        actual = self.cabeza
        while actual is not None:
            if condicion(actual.valor):
                return actual.valor
            actual = actual.siguiente
        return None

    def contiene(self, valor):
        """Indica si el valor está en la lista. O(n)."""
        return self.buscar_por(lambda v: v == valor) is not None

    # ------------------------------------------------------------------
    # Eliminación
    # ------------------------------------------------------------------
    def eliminar_por(self, condicion):
        """Elimina el primer valor que cumple `condicion(valor)`. O(n).

        Devuelve el valor eliminado, o None si ninguno cumple la condición.
        Para quitar un nodo basta con que su anterior apunte al siguiente:

            anterior -> actual -> siguiente   pasa a   anterior -> siguiente
        """
        anterior = None
        actual = self.cabeza
        while actual is not None:
            if condicion(actual.valor):
                if anterior is None:          # era la cabeza
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                if actual is self.cola:       # era el último
                    self.cola = anterior
                self._tamano -= 1
                return actual.valor
            anterior = actual
            actual = actual.siguiente
        return None

    def eliminar(self, valor):
        """Elimina la primera aparición del valor. Devuelve True si lo encontró. O(n)."""
        return self.eliminar_por(lambda v: v == valor) is not None

    # ------------------------------------------------------------------
    # Recorrido y tamaño
    # ------------------------------------------------------------------
    def __iter__(self):
        """Recorre los valores desde la cabeza hasta el final. O(n).

        Permite escribir: for publicacion in lista: ...
        """
        actual = self.cabeza
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def __len__(self):
        """Cantidad de elementos. O(1)."""
        return self._tamano

    def esta_vacia(self):
        """True si no tiene elementos. O(1)."""
        return self._tamano == 0

    def __repr__(self):
        valores = " -> ".join(repr(v) for v in self)
        return f"ListaEnlazada({valores} -> None)" if valores else "ListaEnlazada(vacía)"
