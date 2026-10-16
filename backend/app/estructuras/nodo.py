class Nodo:
    """Nodo de una lista enlazada: guarda un valor y apunta al siguiente nodo."""

    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente

    def __repr__(self):
        return f"Nodo({self.valor!r})"
