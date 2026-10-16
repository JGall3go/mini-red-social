from app.estructuras.trie import Trie


def crear_trie():
    trie = Trie()
    for nombre in ("juan", "julia", "julian", "maria", "mario"):
        trie.insertar(nombre)
    return trie


def test_trie_vacio():
    trie = Trie()
    assert len(trie) == 0
    assert not trie.buscar("juan")
    assert trie.autocompletar("j") == []


def test_buscar_palabras_insertadas():
    trie = crear_trie()
    assert trie.buscar("juan")
    assert trie.buscar("julian")
    assert len(trie) == 5


def test_un_prefijo_no_cuenta_como_palabra():
    trie = crear_trie()
    assert not trie.buscar("jul")
    assert not trie.buscar("pedro")


def test_autocompletar_en_orden_alfabetico():
    trie = crear_trie()
    assert trie.autocompletar("ju") == ["juan", "julia", "julian"]
    assert trie.autocompletar("mar") == ["maria", "mario"]


def test_autocompletar_sin_resultados():
    trie = crear_trie()
    assert trie.autocompletar("z") == []


def test_autocompletar_respeta_el_limite():
    trie = crear_trie()
    assert trie.autocompletar("", limite=2) == ["juan", "julia"]


def test_no_distingue_mayusculas():
    trie = Trie()
    trie.insertar("Juan")
    assert trie.buscar("JUAN")
    assert trie.autocompletar("JU") == ["juan"]


def test_insertar_repetido_no_aumenta_el_tamano():
    trie = Trie()
    trie.insertar("ana")
    trie.insertar("ana")
    assert len(trie) == 1


def test_eliminar_palabra_que_es_prefijo_de_otra():
    trie = crear_trie()
    assert trie.eliminar("julia")
    assert not trie.buscar("julia")
    assert trie.buscar("julian")  # "julian" no se debe borrar
    assert len(trie) == 4


def test_eliminar_borra_los_nodos_que_sobran():
    trie = Trie()
    trie.insertar("sol")
    trie.insertar("sal")
    trie.eliminar("sol")
    assert "o" not in trie.raiz.hijos["s"].hijos
    assert trie.buscar("sal")


def test_eliminar_palabra_inexistente():
    trie = crear_trie()
    assert not trie.eliminar("pedro")
    assert not trie.eliminar("jul")
    assert len(trie) == 5
