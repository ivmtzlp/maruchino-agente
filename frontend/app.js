const form = document.getElementById("form-chat");
const entrada = document.getElementById("entrada");
const contenedor = document.getElementById("mensajes");
const btnEnviar = document.getElementById("btn-enviar");

function agregarMensaje(texto, clase) {
  const div = document.createElement("div");
  div.className = `mensaje ${clase}`;
  div.textContent = texto;
  contenedor.appendChild(div);
  contenedor.scrollTop = contenedor.scrollHeight;
  return div;
}

function agregarCitaciones(citas) {
  if (!citas || citas.length === 0) return;
  const div = document.createElement("div");
  div.className = "citaciones";
  div.innerHTML = "<strong>Fuentes:</strong> " +
    citas.map(c => `<span>${c.fuente.split("/").pop()}</span>`).join(", ");
  contenedor.appendChild(div);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const pregunta = entrada.value.trim();
  if (!pregunta) return;

  agregarMensaje(pregunta, "usuario");
  entrada.value = "";
  btnEnviar.disabled = true;

  const cargando = agregarMensaje("Pensando...", "bot cargando");

  try {
    const resp = await fetch(`${API_URL}/preguntar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: pregunta }),
    });

    if (!resp.ok) throw new Error(`Error ${resp.status}`);

    const data = await resp.json();
    cargando.remove();
    agregarMensaje(data.respuesta, "bot");
    agregarCitaciones(data.citaciones);
  } catch (err) {
    cargando.remove();
    agregarMensaje("⚠️ No pude conectar con el servidor. Revisa que la API esté activa.", "bot error");
    console.error(err);
  } finally {
    btnEnviar.disabled = false;
    entrada.focus();
  }
});