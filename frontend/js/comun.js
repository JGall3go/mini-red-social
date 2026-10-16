// Funciones que usan todas las páginas.

// No hay login: el usuario "actual" se guarda en el navegador
function usuarioActual() {
  const guardado = localStorage.getItem("usuario_actual");
  return guardado ? JSON.parse(guardado) : null;
}

function guardarUsuarioActual(usuario) {
  if (usuario) localStorage.setItem("usuario_actual", JSON.stringify(usuario));
  else localStorage.removeItem("usuario_actual");
}

// Crea un elemento con texto. Se usa textContent para no meter HTML de los usuarios en la página.
function crear(etiqueta, texto, clase) {
  const elemento = document.createElement(etiqueta);
  if (texto !== undefined && texto !== null) elemento.textContent = texto;
  if (clase) elemento.className = clase;
  return elemento;
}

function boton(texto, alHacerClic, clase) {
  const b = crear("button", texto, clase);
  b.addEventListener("click", alHacerClic);
  return b;
}

function mostrarMensaje(texto, esError) {
  const caja = document.getElementById("mensaje");
  if (!caja) return alert(texto);
  caja.textContent = texto;
  caja.className = esError ? "mensaje error" : "mensaje ok";
  setTimeout(() => (caja.className = "mensaje oculto"), 3500);
}

function fechaLegible(iso) {
  return new Date(iso).toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
}

// Tarjeta pequeña de un usuario con enlace a su perfil
function tarjetaUsuario(usuario) {
  const enlace = crear("a", null, "usuario");
  enlace.href = `perfil.html?id=${usuario.id}`;
  enlace.appendChild(crear("strong", usuario.nombre_visible));
  enlace.appendChild(crear("span", "@" + usuario.nombre_usuario, "secundario"));
  return enlace;
}

// Muestra en la barra quién es el usuario actual
function pintarBarra() {
  const zona = document.getElementById("usuario-barra");
  if (!zona) return;
  const yo = usuarioActual();
  zona.textContent = "";
  if (yo) {
    const enlace = crear("a", "@" + yo.nombre_usuario);
    enlace.href = `perfil.html?id=${yo.id}`;
    zona.appendChild(enlace);
    zona.appendChild(boton("Salir", () => {
      guardarUsuarioActual(null);
      location.href = "index.html";
    }, "pequeno"));
  } else {
    zona.appendChild(crear("span", "Sin usuario", "secundario"));
  }
}

document.addEventListener("DOMContentLoaded", pintarBarra);
