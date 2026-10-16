const formUsuario = document.getElementById("form-usuario");
const buscador = document.getElementById("buscador");
const resultados = document.getElementById("resultados");
const listaUsuarios = document.getElementById("lista-usuarios");

async function cargarUsuarios() {
  try {
    const usuarios = await api.listarUsuarios();
    listaUsuarios.textContent = "";
    if (usuarios.length === 0) {
      listaUsuarios.appendChild(crear("li", "Todavía no hay usuarios.", "secundario"));
    }
    for (const usuario of usuarios) {
      const fila = crear("li");
      fila.appendChild(tarjetaUsuario(usuario));
      fila.appendChild(boton("Entrar", () => {
        guardarUsuarioActual(usuario);
        location.href = `perfil.html?id=${usuario.id}`;
      }, "pequeno"));
      listaUsuarios.appendChild(fila);
    }
  } catch (error) {
    mostrarMensaje("No se pudo conectar con la API: " + error.message, true);
  }
}

formUsuario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    const nuevo = await api.crearUsuario({
      nombre_usuario: document.getElementById("nombre_usuario").value.trim(),
      nombre_visible: document.getElementById("nombre_visible").value.trim(),
      biografia: document.getElementById("biografia").value.trim() || null,
    });
    guardarUsuarioActual(nuevo);
    location.href = `perfil.html?id=${nuevo.id}`;
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
});

// Autocompletado: cada vez que se escribe se consulta el Trie del backend
buscador.addEventListener("input", async () => {
  const prefijo = buscador.value.trim();
  resultados.textContent = "";
  if (prefijo === "") return;
  try {
    const encontrados = await api.buscarUsuarios(prefijo);
    if (buscador.value.trim() !== prefijo) return; // ya se escribió otra cosa
    for (const usuario of encontrados) {
      const fila = crear("li");
      fila.appendChild(tarjetaUsuario(usuario));
      resultados.appendChild(fila);
    }
    if (encontrados.length === 0) resultados.appendChild(crear("li", "Sin resultados", "secundario"));
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
});

cargarUsuarios();
