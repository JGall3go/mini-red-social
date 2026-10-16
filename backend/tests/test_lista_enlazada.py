from app.estructuras.lista_enlazada import ListaEnlazada


def test_lista_nueva_esta_vacia():
    lista = ListaEnlazada()
    assert lista.esta_vacia()
    assert len(lista) == 0
    assert list(lista) == []
    assert lista.cabeza is None and lista.cola is None


def test_insertar_inicio_deja_el_mas_reciente_primero():
    lista = ListaEnlazada()
    lista.insertar_inicio("post 1")
    lista.insertar_inicio("post 2")
    lista.insertar_inicio("post 3")
    assert list(lista) == ["post 3", "post 2", "post 1"]
    assert len(lista) == 3
    assert lista.cola.valor == "post 1"


def test_insertar_final_conserva_el_orden_de_llegada():
    lista = ListaEnlazada()
    for valor in (1, 2, 3):
        lista.insertar_final(valor)
    assert list(lista) == [1, 2, 3]
    assert lista.cabeza.valor == 1
    assert lista.cola.valor == 3


def test_mezclar_inserciones_al_inicio_y_al_final():
    lista = ListaEnlazada()
    lista.insertar_final(2)
    lista.insertar_inicio(1)
    lista.insertar_final(3)
    assert list(lista) == [1, 2, 3]


def test_buscar_por_condicion():
    lista = ListaEnlazada()
    lista.insertar_final({"id": 1, "texto": "hola"})
    lista.insertar_final({"id": 2, "texto": "mundo"})
    encontrado = lista.buscar_por(lambda p: p["id"] == 2)
    assert encontrado["texto"] == "mundo"
    assert lista.buscar_por(lambda p: p["id"] == 99) is None


def test_contiene():
    lista = ListaEnlazada()
    lista.insertar_final("ana")
    assert lista.contiene("ana")
    assert not lista.contiene("beto")


def test_eliminar_la_cabeza():
    lista = ListaEnlazada()
    for valor in (1, 2, 3):
        lista.insertar_final(valor)
    assert lista.eliminar(1)
    assert list(lista) == [2, 3]
    assert lista.cabeza.valor == 2


def test_eliminar_del_medio():
    lista = ListaEnlazada()
    for valor in (1, 2, 3):
        lista.insertar_final(valor)
    assert lista.eliminar(2)
    assert list(lista) == [1, 3]
    assert len(lista) == 2


def test_eliminar_el_ultimo_actualiza_la_cola():
    lista = ListaEnlazada()
    for valor in (1, 2, 3):
        lista.insertar_final(valor)
    assert lista.eliminar(3)
    assert lista.cola.valor == 2
    lista.insertar_final(4)  # la cola debe seguir funcionando bien
    assert list(lista) == [1, 2, 4]


def test_eliminar_el_unico_elemento_deja_la_lista_vacia():
    lista = ListaEnlazada()
    lista.insertar_final("solo")
    assert lista.eliminar("solo")
    assert lista.esta_vacia()
    assert lista.cabeza is None and lista.cola is None


def test_eliminar_valor_inexistente_no_cambia_nada():
    lista = ListaEnlazada()
    lista.insertar_final(1)
    assert not lista.eliminar(99)
    assert ListaEnlazada().eliminar(1) is False  # lista vacía
    assert list(lista) == [1]


def test_eliminar_por_devuelve_el_valor_eliminado():
    lista = ListaEnlazada()
    lista.insertar_final({"id": 5})
    eliminado = lista.eliminar_por(lambda p: p["id"] == 5)
    assert eliminado == {"id": 5}
    assert lista.esta_vacia()


def test_representacion_legible():
    lista = ListaEnlazada()
    assert repr(lista) == "ListaEnlazada(vacía)"
    lista.insertar_final(1)
    lista.insertar_final(2)
    assert repr(lista) == "ListaEnlazada(1 -> 2 -> None)"
