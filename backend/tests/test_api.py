def crear(cliente, nombre):
    respuesta = cliente.post("/usuarios", json={"nombre_usuario": nombre, "nombre_visible": nombre.title()})
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def hacer_amigos(cliente, a, b):
    cliente.post("/solicitudes", json={"emisor_id": a, "receptor_id": b})
    assert cliente.post(f"/usuarios/{b}/solicitudes/aceptar").status_code == 200


def test_salud(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok"}


def test_crear_y_buscar_usuarios_con_el_trie(cliente):
    crear(cliente, "juan")
    crear(cliente, "julia")
    crear(cliente, "maria")
    nombres = [u["nombre_usuario"] for u in cliente.get("/usuarios/buscar?prefijo=ju").json()]
    assert nombres == ["juan", "julia"]


def test_usuario_repetido_e_invalido(cliente):
    crear(cliente, "juan")
    assert cliente.post("/usuarios", json={"nombre_usuario": "juan", "nombre_visible": "X"}).status_code == 409
    assert cliente.post("/usuarios", json={"nombre_usuario": "a b", "nombre_visible": "X"}).status_code == 422


def test_usuario_inexistente_da_404(cliente):
    assert cliente.get("/usuarios/99").status_code == 404


def test_actualizar_y_eliminar_usuario(cliente):
    juan = crear(cliente, "juan")
    assert cliente.put(f"/usuarios/{juan}", json={"biografia": "Hola"}).json()["biografia"] == "Hola"
    assert cliente.delete(f"/usuarios/{juan}").status_code == 204
    assert cliente.get("/usuarios/buscar?prefijo=ju").json() == []


def test_solicitudes_se_responden_en_orden_fifo(cliente):
    ana, beto, carla = crear(cliente, "ana"), crear(cliente, "beto"), crear(cliente, "carla")
    cliente.post("/solicitudes", json={"emisor_id": ana, "receptor_id": carla})
    cliente.post("/solicitudes", json={"emisor_id": beto, "receptor_id": carla})
    pendientes = cliente.get(f"/usuarios/{carla}/solicitudes").json()
    assert [s["emisor_id"] for s in pendientes] == [ana, beto]

    aceptada = cliente.post(f"/usuarios/{carla}/solicitudes/aceptar").json()
    assert aceptada["emisor_id"] == ana  # sale primero la más antigua
    cliente.post(f"/usuarios/{carla}/solicitudes/rechazar")
    assert cliente.get(f"/usuarios/{carla}/solicitudes").json() == []
    assert [u["id"] for u in cliente.get(f"/usuarios/{carla}/amigos").json()] == [ana]
    assert cliente.post(f"/usuarios/{carla}/solicitudes/aceptar").status_code == 400


def test_sugerencias_y_grados_con_el_grafo(cliente):
    ana, beto, carla, dani = (crear(cliente, n) for n in ("ana", "beto", "carla", "dani"))
    hacer_amigos(cliente, ana, beto)
    hacer_amigos(cliente, beto, carla)
    hacer_amigos(cliente, carla, dani)
    assert [u["id"] for u in cliente.get(f"/usuarios/{ana}/sugerencias").json()] == [carla]
    grados = cliente.get(f"/grados?origen={ana}&destino={dani}").json()
    assert grados["grados"] == 3
    assert [u["id"] for u in grados["camino"]] == [ana, beto, carla, dani]
    assert len(cliente.get("/grafo").json()["aristas"]) == 3


def test_feed_por_fecha_y_por_likes(cliente):
    ana, beto = crear(cliente, "ana"), crear(cliente, "beto")
    hacer_amigos(cliente, ana, beto)
    p1 = cliente.post("/publicaciones", json={"autor_id": ana, "contenido": "primero"}).json()["id"]
    p2 = cliente.post("/publicaciones", json={"autor_id": beto, "contenido": "segundo"}).json()["id"]
    p3 = cliente.post("/publicaciones", json={"autor_id": ana, "contenido": "tercero"}).json()["id"]
    cliente.post(f"/publicaciones/{p1}/like", json={"usuario_id": beto})

    por_fecha = [p["id"] for p in cliente.get(f"/usuarios/{ana}/feed?orden=fecha").json()]
    assert por_fecha == [p3, p2, p1]
    por_likes = [p["id"] for p in cliente.get(f"/usuarios/{ana}/feed?orden=likes").json()]
    assert por_likes[0] == p1


def test_like_editar_y_borrar_publicacion(cliente):
    ana, beto = crear(cliente, "ana"), crear(cliente, "beto")
    post = cliente.post("/publicaciones", json={"autor_id": ana, "contenido": "hola"}).json()["id"]
    assert cliente.post(f"/publicaciones/{post}/like", json={"usuario_id": beto}).json()["total_likes"] == 1
    assert cliente.post(f"/publicaciones/{post}/like", json={"usuario_id": beto}).status_code == 400
    assert cliente.delete(f"/publicaciones/{post}/like?usuario_id={beto}").json()["total_likes"] == 0
    assert cliente.get(f"/usuarios/{beto}/likes").json() == []
    assert cliente.put(f"/publicaciones/{post}", json={"contenido": "editado"}).json()["contenido"] == "editado"
    assert cliente.delete(f"/publicaciones/{post}").status_code == 204
    assert cliente.get(f"/usuarios/{ana}/publicaciones").json() == []
    assert cliente.get("/estructuras/bst").json()["nodos"] == []


def test_vistas_de_estructuras(cliente):
    ana = crear(cliente, "ana")
    crear(cliente, "andres")
    trie = cliente.get("/estructuras/trie?prefijo=an").json()
    finales = {n["id"] for n in trie["nodos"] if n["es_fin"]}
    assert finales == {"ana", "andres"}
    cliente.post("/publicaciones", json={"autor_id": ana, "contenido": "hola"})
    assert len(cliente.get(f"/estructuras/lista/{ana}").json()) == 1
    assert cliente.get("/estructuras/bst").json()["altura"] == 1


def test_las_estructuras_se_recargan_desde_la_bd(cliente, sesion):
    from app.servicios.red_social import red

    ana, beto = crear(cliente, "ana"), crear(cliente, "beto")
    hacer_amigos(cliente, ana, beto)
    cliente.post("/publicaciones", json={"autor_id": ana, "contenido": "hola"})
    red.cargar(sesion)  # como si se reiniciara el servidor
    assert [u["id"] for u in cliente.get(f"/usuarios/{ana}/amigos").json()] == [beto]
    assert len(cliente.get(f"/usuarios/{beto}/feed").json()) == 1


def test_cada_usuario_ve_sus_propios_likes(cliente, sesion):
    from app.servicios.red_social import red

    ana, beto, carla = crear(cliente, "ana"), crear(cliente, "beto"), crear(cliente, "carla")
    post = cliente.post("/publicaciones", json={"autor_id": ana, "contenido": "hola"}).json()["id"]
    cliente.post(f"/publicaciones/{post}/like", json={"usuario_id": beto})
    assert cliente.get(f"/usuarios/{beto}/likes").json() == [post]
    # carla no ha dado like, así que puede darlo aunque el post ya tenga uno
    assert cliente.get(f"/usuarios/{carla}/likes").json() == []
    assert cliente.post(f"/publicaciones/{post}/like", json={"usuario_id": carla}).json()["total_likes"] == 2
    red.cargar(sesion)  # al reiniciar se vuelven a cargar desde la BD
    assert cliente.get(f"/usuarios/{carla}/likes").json() == [post]
    cliente.delete(f"/publicaciones/{post}")
    assert cliente.get(f"/usuarios/{beto}/likes").json() == []
