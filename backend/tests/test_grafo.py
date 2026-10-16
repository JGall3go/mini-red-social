import pytest

from app.estructuras.grafo import Grafo


def crear_grafo():
    # 1 - 2 - 4 - 5
    # |   |
    # 3 --+        6 (sin amigos)
    grafo = Grafo()
    for a, b in ((1, 2), (1, 3), (2, 3), (2, 4), (4, 5)):
        grafo.agregar_arista(a, b)
    grafo.agregar_vertice(6)
    return grafo


def test_agregar_arista_es_en_las_dos_direcciones():
    grafo = crear_grafo()
    assert grafo.son_amigos(1, 2)
    assert grafo.son_amigos(2, 1)
    assert not grafo.son_amigos(1, 4)


def test_no_se_repiten_amistades():
    grafo = crear_grafo()
    assert not grafo.agregar_arista(1, 2)
    assert grafo.vecinos(1) == [2, 3]


def test_no_puede_ser_amigo_de_si_mismo():
    with pytest.raises(ValueError):
        Grafo().agregar_arista(1, 1)


def test_vecinos():
    grafo = crear_grafo()
    assert grafo.vecinos(2) == [1, 3, 4]
    assert grafo.vecinos(6) == []
    assert grafo.vecinos(99) == []


def test_eliminar_arista():
    grafo = crear_grafo()
    assert grafo.eliminar_arista(2, 4)
    assert not grafo.son_amigos(4, 2)
    assert not grafo.eliminar_arista(2, 4)


def test_eliminar_vertice_lo_quita_de_sus_amigos():
    grafo = crear_grafo()
    assert grafo.eliminar_vertice(2)
    assert 2 not in grafo.vecinos(1)
    assert 2 not in grafo.vecinos(4)
    assert len(grafo) == 5
    assert not grafo.eliminar_vertice(99)


def test_bfs_recorre_por_niveles():
    grafo = crear_grafo()
    assert grafo.bfs(1) == [1, 2, 3, 4, 5]
    assert grafo.bfs(6) == [6]
    assert grafo.bfs(99) == []


def test_sugerencias_son_amigos_de_amigos():
    grafo = crear_grafo()
    assert grafo.sugerencias(1) == [4]
    assert grafo.sugerencias(5) == [2]
    assert grafo.sugerencias(6) == []


def test_sugerencias_ordenadas_por_amigos_en_comun():
    grafo = Grafo()
    # 7 tiene 2 amigos en común con 1 (2 y 3); 8 solo tiene 1 (2)
    for a, b in ((1, 2), (1, 3), (2, 7), (3, 7), (2, 8)):
        grafo.agregar_arista(a, b)
    assert grafo.sugerencias(1) == [7, 8]
    assert grafo.sugerencias(1, limite=1) == [7]


def test_grados_de_separacion():
    grafo = crear_grafo()
    assert grafo.grados_separacion(1, 5) == [1, 2, 4, 5]  # 3 grados
    assert grafo.grados_separacion(1, 2) == [1, 2]  # 1 grado
    assert grafo.grados_separacion(3, 3) == [3]  # 0 grados


def test_grados_sin_conexion():
    grafo = crear_grafo()
    assert grafo.grados_separacion(1, 6) is None
    assert grafo.grados_separacion(1, 99) is None


def test_aristas_sin_repetir():
    grafo = crear_grafo()
    assert sorted(grafo.aristas()) == [(1, 2), (1, 3), (2, 3), (2, 4), (4, 5)]
