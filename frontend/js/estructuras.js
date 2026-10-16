// Opciones para dibujar árboles de arriba hacia abajo con vis-network
const opcionesArbol = {
  layout: { hierarchical: { direction: "UD", sortMethod: "directed", levelSeparation: 70, nodeSpacing: 90 } },
  physics: false,
  nodes: { shape: "box", margin: 8, color: { background: "#eef3fc", border: "#2f6fde" } },
  edges: { arrows: "to", color: "#9aa5b8" },
};

let redTrie = null;
let redBst = null;

async function dibujarTrie() {
  const prefijo = document.getElementById("prefijo-trie").value.trim();
  try {
    const datos = await api.verTrie(prefijo);
    const nodos = datos.nodos.map((n) => ({
      id: n.id,
      label: n.label,
      // Verde si ahí termina un nombre de usuario
      color: n.es_fin ? { background: "#dff3e6", border: "#2e8b57" } : undefined,
    }));
    if (redTrie) redTrie.destroy();
    redTrie = new vis.Network(document.getElementById("lienzo-trie"), { nodes: nodos, edges: datos.aristas }, opcionesArbol);
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

async function dibujarBst() {
  try {
    const datos = await api.verBst();
    document.getElementById("altura-bst").textContent =
      `${datos.nodos.length} publicaciones · altura del árbol: ${datos.altura}`;
    const aristas = datos.aristas.map((a) => ({ from: a.from, to: a.to, label: a.lado }));
    if (redBst) redBst.destroy();
    redBst = new vis.Network(document.getElementById("lienzo-bst"), { nodes: datos.nodos, edges: aristas }, opcionesArbol);
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

// Dibuja una lista de textos como cajas unidas por flechas
function dibujarCadena(contenedor, textos, inicio, fin) {
  contenedor.textContent = "";
  contenedor.appendChild(crear("span", inicio, "etiqueta"));
  textos.forEach((texto, i) => {
    contenedor.appendChild(crear("span", texto, "caja"));
    if (i < textos.length - 1) contenedor.appendChild(crear("span", "→", "flecha"));
  });
  if (textos.length === 0) contenedor.appendChild(crear("span", "(vacía)", "secundario"));
  contenedor.appendChild(crear("span", fin, "etiqueta"));
}

async function dibujarColaYLista() {
  const id = document.getElementById("usuario-estructuras").value;
  if (!id) return;
  try {
    const cola = await api.verCola(id);
    dibujarCadena(document.getElementById("vista-cola"),
      cola.map((s) => "de @" + s.emisor.nombre_usuario), "frente →", "← final");
    const lista = await api.verLista(id);
    dibujarCadena(document.getElementById("vista-lista"),
      lista.map((p) => p.contenido), "cabeza →", "→ None");
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

async function iniciar() {
  try {
    const usuarios = await api.listarUsuarios();
    const selector = document.getElementById("usuario-estructuras");
    for (const u of usuarios) {
      const opcion = crear("option", "@" + u.nombre_usuario);
      opcion.value = u.id;
      selector.appendChild(opcion);
    }
    const yo = usuarioActual();
    if (yo) selector.value = yo.id;
    selector.addEventListener("change", dibujarColaYLista);
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
  document.getElementById("prefijo-trie").addEventListener("input", dibujarTrie);
  dibujarTrie();
  dibujarBst();
  dibujarColaYLista();
}

iniciar();
