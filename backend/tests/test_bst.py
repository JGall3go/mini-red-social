from app.estructuras.bst import BST


def crear_bst():
    #        50
    #      /    \
    #    30      70
    #   /  \    /  \
    #  20  40  60  80
    bst = BST()
    for clave in (50, 30, 70, 20, 40, 60, 80):
        bst.insertar(clave, f"post {clave}")
    return bst


def test_bst_vacio():
    bst = BST()
    assert bst.esta_vacio()
    assert bst.inorden() == []
    assert bst.buscar(10) is None
    assert bst.altura() == 0


def test_inorden_devuelve_ordenado():
    bst = crear_bst()
    assert bst.inorden() == [f"post {c}" for c in (20, 30, 40, 50, 60, 70, 80)]


def test_inorden_inverso_devuelve_de_mayor_a_menor():
    bst = crear_bst()
    assert bst.inorden_inverso() == [f"post {c}" for c in (80, 70, 60, 50, 40, 30, 20)]


def test_buscar():
    bst = crear_bst()
    assert bst.buscar(60) == "post 60"
    assert bst.buscar(65) is None


def test_insertar_clave_repetida_actualiza_el_valor():
    bst = crear_bst()
    bst.insertar(40, "editado")
    assert bst.buscar(40) == "editado"
    assert len(bst) == 7


def test_eliminar_hoja():
    bst = crear_bst()
    assert bst.eliminar(20)
    assert bst.buscar(20) is None
    assert len(bst) == 6


def test_eliminar_nodo_con_un_hijo():
    bst = crear_bst()
    bst.eliminar(20)
    assert bst.eliminar(30)  # ahora 30 solo tiene a 40
    assert bst.inorden() == [f"post {c}" for c in (40, 50, 60, 70, 80)]


def test_eliminar_nodo_con_dos_hijos():
    bst = crear_bst()
    assert bst.eliminar(70)
    assert bst.raiz.derecho.clave == 80  # el sucesor de 70 es 80
    assert bst.inorden() == [f"post {c}" for c in (20, 30, 40, 50, 60, 80)]


def test_eliminar_la_raiz():
    bst = crear_bst()
    assert bst.eliminar(50)
    assert bst.raiz.clave == 60
    assert bst.inorden() == [f"post {c}" for c in (20, 30, 40, 60, 70, 80)]


def test_eliminar_clave_inexistente():
    bst = crear_bst()
    assert not bst.eliminar(99)
    assert len(bst) == 7


def test_claves_tupla_para_publicaciones():
    # (likes, fecha, id): con los mismos likes desempata la fecha
    bst = BST()
    bst.insertar((5, "2026-10-01", 1), "A")
    bst.insertar((10, "2026-10-02", 2), "B")
    bst.insertar((5, "2026-10-03", 3), "C")
    assert bst.inorden_inverso() == ["B", "C", "A"]


def test_altura_balanceado_y_degenerado():
    assert crear_bst().altura() == 3
    bst = BST()
    for clave in range(1, 6):  # claves ya ordenadas
        bst.insertar(clave, clave)
    assert bst.altura() == 5  # queda como una lista
