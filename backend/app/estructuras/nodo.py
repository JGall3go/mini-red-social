"""Nodo simple enlazado, base de la Lista enlazada y de la Cola."""


class Nodo:
    """Caja que guarda un valor y una referencia al nodo siguiente.

    Una lista enlazada o una cola no son más que una cadena de nodos:

        [valor | siguiente] -> [valor | siguiente] -> None

    Al no usar un arreglo, no hay que mover elementos ni reservar espacio:
    agregar o quitar un nodo solo consiste en cambiar referencias.
    """

    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente

    def __repr__(self):
        return f"Nodo({self.valor!r})"
