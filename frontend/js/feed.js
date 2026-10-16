const yo = usuarioActual();
const selectorOrden = document.getElementById("orden");
const contenedor = document.getElementById("feed");

// Ids de los posts a los que el usuario actual les dio like (se piden a la API)
let misLikes = new Set();

async function alternarLike(post) {
  try {
    if (misLikes.has(post.id)) await api.quitarLike(post.id, yo.id);
    else await api.darLike(post.id, yo.id);
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
  cargarFeed();
}

async function cargarFeed() {
  contenedor.textContent = "";
  if (!yo) {
    contenedor.appendChild(crear("p", "Entra con un usuario desde Inicio para ver tu feed.", "secundario"));
    return;
  }
  try {
    const [publicaciones, usuarios, likes] = await Promise.all([
      api.feed(yo.id, selectorOrden.value), api.listarUsuarios(), api.likesDe(yo.id),
    ]);
    misLikes = new Set(likes);
    const nombres = {};
    usuarios.forEach((u) => (nombres[u.id] = u));
    if (publicaciones.length === 0) {
      contenedor.appendChild(crear("p", "No hay publicaciones todavía. ¡Agrega amigos o publica algo!", "secundario"));
    }
    for (const post of publicaciones) {
      const caja = crear("article", null, "post");
      const cabecera = crear("div", null, "cabecera");
      cabecera.appendChild(tarjetaUsuario(nombres[post.autor_id]));
      cabecera.appendChild(crear("span", fechaLegible(post.creada_en), "secundario"));
      caja.appendChild(cabecera);
      caja.appendChild(crear("p", post.contenido));
      const texto = (misLikes.has(post.id) ? "Quitar like" : "Me gusta") + ` (${post.total_likes})`;
      caja.appendChild(boton(texto, () => alternarLike(post), misLikes.has(post.id) ? "pequeno" : "pequeno secundario"));
      contenedor.appendChild(caja);
    }
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

selectorOrden.addEventListener("change", cargarFeed);
cargarFeed();
