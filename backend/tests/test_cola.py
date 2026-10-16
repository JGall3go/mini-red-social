import pytest

from app.estructuras.cola import Cola


def test_cola_nueva_esta_vacia():
    cola = Cola()
    assert cola.esta_vacia()
    assert len(cola) == 0
    assert list(cola) == []


def test_sale_primero_el_que_entro_primero():
    cola = Cola()
    cola.encolar("ana")
    cola.encolar("beto")
    cola.encolar("carla")
    assert cola.desencolar() == "ana"
    assert cola.desencolar() == "beto"
    assert cola.desencolar() == "carla"
    assert cola.esta_vacia()


def test_ver_frente_no_saca_el_elemento():
    cola = Cola()
    cola.encolar(1)
    cola.encolar(2)
    assert cola.ver_frente() == 1
    assert len(cola) == 2


def test_recorrer_en_orden_sin_modificar():
    cola = Cola()
    for valor in (1, 2, 3):
        cola.encolar(valor)
    assert list(cola) == [1, 2, 3]
    assert len(cola) == 3


def test_desencolar_cola_vacia_lanza_error():
    with pytest.raises(IndexError):
        Cola().desencolar()


def test_ver_frente_cola_vacia_lanza_error():
    with pytest.raises(IndexError):
        Cola().ver_frente()


def test_se_puede_reusar_despues_de_vaciarla():
    cola = Cola()
    cola.encolar(1)
    cola.desencolar()
    assert cola.final is None
    cola.encolar(2)
    assert cola.ver_frente() == 2
    assert list(cola) == [2]


def test_representacion_legible():
    cola = Cola()
    cola.encolar(1)
    cola.encolar(2)
    assert repr(cola) == "Cola(frente -> [1, 2] <- final)"
