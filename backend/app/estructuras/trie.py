"""Trie (árbol de prefijos) para buscar usuarios con autocompletado.

Cada nodo representa una letra. Las palabras que comparten el inicio
comparten también el camino desde la raíz, por ejemplo "juan" y "julia"
comparten "j" -> "u".

Las palabras se guardan en minúscula para que la búsqueda no distinga
mayúsculas.

Complejidad (m = largo de la palabra o prefijo):
    insertar      O(m)
    buscar        O(m)
    eliminar      O(m)
    autocompletar O(m + k)  (k = nodos que hay debajo del prefijo)
"""


class NodoTrie:
    def __init__(self):
        self.hijos = {}  # letra -> NodoTrie
        self.es_fin = False  # True si aquí termina una palabra


class Trie:
    def __init__(self):
        self.raiz = NodoTrie()
        self._tamano = 0

    def insertar(self, palabra):
        # Baja letra por letra creando los nodos que falten. O(m)
        nodo = self.raiz
        for letra in palabra.lower():
            if letra not in nodo.hijos:
                nodo.hijos[letra] = NodoTrie()
            nodo = nodo.hijos[letra]
        if not nodo.es_fin:
            nodo.es_fin = True
            self._tamano += 1

    def _buscar_nodo(self, texto):
        # Devuelve el nodo donde termina el texto, o None si no existe. O(m)
        nodo = self.raiz
        for letra in texto.lower():
            if letra not in nodo.hijos:
                return None
            nodo = nodo.hijos[letra]
        return nodo

    def buscar(self, palabra):
        # True solo si la palabra completa fue insertada. O(m)
        nodo = self._buscar_nodo(palabra)
        return nodo is not None and nodo.es_fin

    def autocompletar(self, prefijo, limite=10):
        # Devuelve hasta `limite` palabras que empiezan por el prefijo,
        # en orden alfabético. O(m + k)
        nodo = self._buscar_nodo(prefijo)
        resultados = []
        if nodo is not None:
            self._recolectar(nodo, prefijo.lower(), resultados, limite)
        return resultados

    def _recolectar(self, nodo, palabra_actual, resultados, limite):
        # Recorrido en profundidad desde el nodo, armando las palabras.
        if len(resultados) >= limite:
            return
        if nodo.es_fin:
            resultados.append(palabra_actual)
        for letra in sorted(nodo.hijos):
            self._recolectar(nodo.hijos[letra], palabra_actual + letra, resultados, limite)

    def eliminar(self, palabra):
        # Devuelve True si la palabra existía. O(m)
        if not self.buscar(palabra):
            return False
        self._eliminar(self.raiz, palabra.lower(), 0)
        self._tamano -= 1
        return True

    def _eliminar(self, nodo, palabra, i):
        # Desmarca el final de la palabra y, al volver de la recursión,
        # borra los nodos que ya no forman parte de ninguna otra palabra.
        # Devuelve True si el nodo quedó sin uso y se puede borrar.
        if i == len(palabra):
            nodo.es_fin = False
            return len(nodo.hijos) == 0
        letra = palabra[i]
        if self._eliminar(nodo.hijos[letra], palabra, i + 1):
            del nodo.hijos[letra]
        return not nodo.es_fin and len(nodo.hijos) == 0

    def __len__(self):
        return self._tamano
