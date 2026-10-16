const parametros = new URLSearchParams(location.search);
const perfilId = Number(parametros.get("id"));
const yo = usuarioActual();
const esMiPerfil = yo && yo.id === perfilId;

function pintarPublicacion(post, contenedor) {
  const caja = crear("article", null, "post");
  const cabecera = crear("div", null, "cabecera");
  cabecera.appendChild(crear("span", fechaLegible(post.creada_en), "secundario"));
  cabecera.appendChild(crear("span", `${post.total_likes} likes`, "secundario"));
  caja.appendChild(cabecera);
  caja.appendChild(crear("p", post.contenido));

  if (esMiPerfil) {
    const acciones = crear("div", null, "acciones");
    acciones.appendChild(boton("Editar", async () => {
      const nuevo = prompt("Nuevo contenido:", post.contenido);
      if (!nuevo) return;
      try {
        await api.editarPublicacion(post.id, nuevo);
        cargarPerfil();
      } catch (error) {
        mostrarMensaje(error.message, true);
      }
    }, "pequeno secundario"));
    acciones.appendChild(boton("Borrar", async () => {
      if (!confirm("¿Borrar esta publicación?")) return;
      await api.eliminarPublicacion(post.id);
      cargarPerfil();
    }, "pequeno peligro"));
    caja.appendChild(acciones);
  }
  contenedor.appendChild(caja);
}

function pintarListaUsuarios(idLista, usuarios, textoVacio, accion) {
  const lista = document.getElementById(idLista);
  lista.textContent = "";
  if (usuarios.length === 0) lista.appendChild(crear("li", textoVacio, "secundario"));
  for (const usuario of usuarios) {
    const fila = crear("li");
    fila.appendChild(tarjetaUsuario(usuario));
    if (accion) fila.appendChild(accion(usuario));
    lista.appendChild(fila);
  }
}

async function enviarSolicitudA(receptorId) {
  try {
    await api.enviarSolicitud(yo.id, receptorId);
    mostrarMensaje("Solicitud enviada");
    cargarPerfil();
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

async function cargarPerfil() {
  try {
    const usuario = await api.obtenerUsuario(perfilId);
    document.getElementById("nombre").textContent = usuario.nombre_visible;
    document.getElementById("datos").textContent =
      `@${usuario.nombre_usuario} · ${usuario.total_amigos} amigos · ${usuario.total_publicaciones} publicaciones`;
    document.getElementById("bio").textContent = usuario.biografia || "";

    const amigos = await api.amigos(perfilId);
    pintarListaUsuarios("amigos", amigos, "Aún no tiene amigos.");

    // Botones según quién está viendo el perfil
    const acciones = document.getElementById("acciones-perfil");
    acciones.textContent = "";
    if (!yo) {
      acciones.appendChild(crear("span", "Entra con un usuario desde Inicio para interactuar.", "secundario"));
    } else if (esMiPerfil) {
      acciones.appendChild(boton("Editar biografía", async () => {
        const bio = prompt("Nueva biografía:", usuario.biografia || "");
        if (bio === null) return;
        await api.actualizarUsuario(perfilId, { biografia: bio });
        cargarPerfil();
      }, "secundario"));
      acciones.appendChild(boton("Eliminar mi cuenta", async () => {
        if (!confirm("Se borrarán tus amistades y publicaciones. ¿Seguro?")) return;
        await api.eliminarUsuario(perfilId);
        guardarUsuarioActual(null);
        location.href = "index.html";
      }, "peligro"));
    } else if (!amigos.some((a) => a.id === yo.id)) {
      acciones.appendChild(boton("Enviar solicitud de amistad", () => enviarSolicitudA(perfilId)));
    }

    // Solo el dueño ve sus solicitudes, sugerencias y el formulario para publicar
    for (const id of ["zona-solicitudes", "zona-sugerencias", "zona-publicar"]) {
      document.getElementById(id).style.display = esMiPerfil ? "" : "none";
    }
    if (esMiPerfil) {
      const solicitudes = await api.solicitudes(perfilId);
      pintarListaUsuarios("solicitudes", solicitudes.map((s) => s.emisor), "No tienes solicitudes.");
      const sugerencias = await api.sugerencias(perfilId);
      pintarListaUsuarios("sugerencias", sugerencias, "No hay sugerencias por ahora.",
        (u) => boton("Agregar", () => enviarSolicitudA(u.id), "pequeno"));
    }

    const publicaciones = await api.publicacionesDe(perfilId);
    const contenedor = document.getElementById("publicaciones");
    contenedor.textContent = "";
    if (publicaciones.length === 0) contenedor.appendChild(crear("p", "Sin publicaciones.", "secundario"));
    publicaciones.forEach((post) => pintarPublicacion(post, contenedor));
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

async function responder(aceptar) {
  try {
    if (aceptar) await api.aceptarSolicitud(perfilId);
    else await api.rechazarSolicitud(perfilId);
    mostrarMensaje(aceptar ? "Solicitud aceptada" : "Solicitud rechazada");
    cargarPerfil();
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

document.getElementById("aceptar").addEventListener("click", () => responder(true));
document.getElementById("rechazar").addEventListener("click", () => responder(false));

document.getElementById("form-publicar").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const campo = document.getElementById("contenido");
  try {
    await api.publicar(perfilId, campo.value.trim());
    campo.value = "";
    cargarPerfil();
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
});

cargarPerfil();
