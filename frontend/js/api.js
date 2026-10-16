// Funciones para hablar con la API. Todas devuelven una promesa con el JSON de respuesta.

async function pedir(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (cuerpo !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo);
  }
  const respuesta = await fetch(API_URL + ruta, opciones);
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json();
  if (!respuesta.ok) {
    // FastAPI manda el error en "detail" (texto o lista de errores de validación)
    const detalle = Array.isArray(datos.detail) ? "Datos inválidos" : datos.detail;
    throw new Error(detalle || "Error en la petición");
  }
  return datos;
}

const api = {
  // Usuarios
  crearUsuario: (datos) => pedir("POST", "/usuarios", datos),
  listarUsuarios: () => pedir("GET", "/usuarios"),
  obtenerUsuario: (id) => pedir("GET", `/usuarios/${id}`),
  actualizarUsuario: (id, datos) => pedir("PUT", `/usuarios/${id}`, datos),
  eliminarUsuario: (id) => pedir("DELETE", `/usuarios/${id}`),
  buscarUsuarios: (prefijo) => pedir("GET", `/usuarios/buscar?prefijo=${encodeURIComponent(prefijo)}`),

  // Amistades
  enviarSolicitud: (emisor_id, receptor_id) => pedir("POST", "/solicitudes", { emisor_id, receptor_id }),
  solicitudes: (id) => pedir("GET", `/usuarios/${id}/solicitudes`),
  aceptarSolicitud: (id) => pedir("POST", `/usuarios/${id}/solicitudes/aceptar`),
  rechazarSolicitud: (id) => pedir("POST", `/usuarios/${id}/solicitudes/rechazar`),
  amigos: (id) => pedir("GET", `/usuarios/${id}/amigos`),
  sugerencias: (id) => pedir("GET", `/usuarios/${id}/sugerencias`),
  grados: (origen, destino) => pedir("GET", `/grados?origen=${origen}&destino=${destino}`),
  grafo: () => pedir("GET", "/grafo"),

  // Publicaciones
  publicar: (autor_id, contenido) => pedir("POST", "/publicaciones", { autor_id, contenido }),
  publicacionesDe: (id) => pedir("GET", `/usuarios/${id}/publicaciones`),
  editarPublicacion: (id, contenido) => pedir("PUT", `/publicaciones/${id}`, { contenido }),
  eliminarPublicacion: (id) => pedir("DELETE", `/publicaciones/${id}`),
  darLike: (id, usuario_id) => pedir("POST", `/publicaciones/${id}/like`, { usuario_id }),
  quitarLike: (id, usuario_id) => pedir("DELETE", `/publicaciones/${id}/like?usuario_id=${usuario_id}`),
  likesDe: (id) => pedir("GET", `/usuarios/${id}/likes`),
  feed: (id, orden) => pedir("GET", `/usuarios/${id}/feed?orden=${orden}`),

  // Vista de estructuras
  verTrie: (prefijo) => pedir("GET", `/estructuras/trie?prefijo=${encodeURIComponent(prefijo)}`),
  verBst: () => pedir("GET", "/estructuras/bst"),
  verCola: (id) => pedir("GET", `/estructuras/cola/${id}`),
  verLista: (id) => pedir("GET", `/estructuras/lista/${id}`),
};
