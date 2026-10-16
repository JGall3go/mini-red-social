let red = null;
let nodos = null;
let aristas = null;

function llenarSelectores(usuarios) {
  for (const id of ["origen", "destino"]) {
    const selector = document.getElementById(id);
    selector.textContent = "";
    for (const u of usuarios) {
      const opcion = crear("option", u.label);
      opcion.value = u.id;
      selector.appendChild(opcion);
    }
  }
  const yo = usuarioActual();
  if (yo) document.getElementById("origen").value = yo.id;
}

async function dibujarGrafo() {
  try {
    const datos = await api.grafo();
    nodos = new vis.DataSet(datos.nodos);
    aristas = new vis.DataSet(datos.aristas.map((a, i) => ({ id: i, ...a })));
    const opciones = {
      nodes: { shape: "dot", size: 16, color: "#2f6fde", font: { size: 14 } },
      edges: { color: "#9aa5b8", width: 2 },
      physics: { stabilization: true },
    };
    red = new vis.Network(document.getElementById("lienzo-grafo"), { nodes: nodos, edges: aristas }, opciones);
    red.on("doubleClick", (evento) => {
      if (evento.nodes.length > 0) location.href = `perfil.html?id=${evento.nodes[0]}`;
    });
    llenarSelectores(datos.nodos);
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

function resaltarCamino(ids) {
  // Primero se quita el resaltado anterior
  nodos.update(nodos.get().map((n) => ({ id: n.id, color: "#2f6fde" })));
  aristas.update(aristas.get().map((a) => ({ id: a.id, color: "#9aa5b8", width: 2 })));
  nodos.update(ids.map((id) => ({ id, color: "#e08a1e" })));
  for (let i = 0; i < ids.length - 1; i++) {
    const arista = aristas.get().find((a) =>
      (a.from === ids[i] && a.to === ids[i + 1]) || (a.from === ids[i + 1] && a.to === ids[i]));
    if (arista) aristas.update({ id: arista.id, color: "#e08a1e", width: 4 });
  }
}

document.getElementById("calcular").addEventListener("click", async () => {
  const origen = document.getElementById("origen").value;
  const destino = document.getElementById("destino").value;
  const salida = document.getElementById("resultado-grados");
  try {
    const resultado = await api.grados(origen, destino);
    if (!resultado.conectados) {
      salida.textContent = "No están conectados.";
      resaltarCamino([]);
      return;
    }
    const nombres = resultado.camino.map((u) => "@" + u.nombre_usuario).join(" → ");
    salida.textContent = `${resultado.grados} grado(s) de separación: ${nombres}`;
    resaltarCamino(resultado.camino.map((u) => u.id));
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
});

dibujarGrafo();
