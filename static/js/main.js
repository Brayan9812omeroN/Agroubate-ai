// main.js — lógica de interfaz de AgroUbaté AI
// Consume la API Flask (/api/...) y actualiza el DOM sin frameworks.

const listaInsumos = document.getElementById("lista-insumos");
const filtroTipo = document.getElementById("filtro-tipo");
const resultadoInsumo = document.getElementById("resultado-insumo");
const tablaLecheBody = document.querySelector("#tabla-leche tbody");
const destacadoLeche = document.getElementById("destacado-leche");

const TIPO_LABEL = {
  concentrado: "Concentrado",
  sal_mineralizada: "Sal mineralizada",
  medicamento: "Medicamento",
};

const formatoCOP = (valor) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(valor);

async function cargarInsumos(tipo = "") {
  const url = tipo ? `/api/insumos?tipo=${encodeURIComponent(tipo)}` : "/api/insumos";
  const res = await fetch(url);
  const insumos = await res.json();

  listaInsumos.innerHTML = "";
  insumos.forEach((insumo) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.dataset.id = insumo.id;
    btn.innerHTML = `${insumo.nombre}<span class="tipo-tag">${TIPO_LABEL[insumo.tipo] || insumo.tipo}</span>`;
    btn.addEventListener("click", () => seleccionarInsumo(insumo.id, btn));
    li.appendChild(btn);
    listaInsumos.appendChild(li);
  });

  if (insumos.length === 0) {
    listaInsumos.innerHTML = "<li><em>No hay insumos para este tipo.</em></li>";
  }
}

async function seleccionarInsumo(id, btnClicado) {
  document
    .querySelectorAll("#lista-insumos button")
    .forEach((b) => b.classList.remove("is-active"));
  btnClicado.classList.add("is-active");

  const res = await fetch(`/api/insumos/${id}/precios`);
  if (!res.ok) {
    resultadoInsumo.innerHTML = "<p class='placeholder'>No fue posible cargar la comparación.</p>";
    return;
  }
  const data = await res.json();

  if (!data.comparacion.length) {
    resultadoInsumo.innerHTML = `<p class="placeholder">Aún no hay precios registrados para ${data.insumo.nombre}.</p>`;
    return;
  }

  const filas = data.comparacion
    .map((p, i) => {
      const esMejor = i === 0 ? "mejor" : "";
      return `<tr class="${esMejor}">
        <td>${p.almacen.nombre}</td>
        <td>${p.almacen.municipio}</td>
        <td>${formatoCOP(p.precio)}</td>
      </tr>`;
    })
    .join("");

  resultadoInsumo.innerHTML = `
    <h3>${data.insumo.nombre}</h3>
    <p class="unidad">Precio por ${data.insumo.unidad}</p>
    <table class="ledger-table">
      <thead>
        <tr><th>Almacén</th><th>Municipio</th><th>Precio</th></tr>
      </thead>
      <tbody>${filas}</tbody>
    </table>
  `;
}

async function cargarPreciosLeche() {
  const res = await fetch("/api/leche/compradores");
  const compradores = await res.json();

  if (!compradores.length) {
    tablaLecheBody.innerHTML = "<tr><td colspan='6'>No hay compradores registrados.</td></tr>";
    return;
  }

  const mejor = compradores[0];
  destacadoLeche.innerHTML = `
    <p class="etiqueta">Mejor pago actual</p>
    <p class="valor">${mejor.comprador.nombre} — ${formatoCOP(mejor.precio_total)} / litro</p>
  `;

  tablaLecheBody.innerHTML = compradores
    .map((p, i) => {
      const esMejor = i === 0 ? "mejor" : "";
      return `<tr class="${esMejor}">
        <td>${p.comprador.nombre}</td>
        <td>${p.comprador.tipo}</td>
        <td>${p.comprador.municipio}</td>
        <td>${formatoCOP(p.precio_litro)}</td>
        <td>${formatoCOP(p.bonificacion)}</td>
        <td>${formatoCOP(p.precio_total)}</td>
      </tr>`;
    })
    .join("");
}

filtroTipo.addEventListener("change", (e) => {
  resultadoInsumo.innerHTML = "<p class='placeholder'>Seleccione un insumo de la lista para comparar precios.</p>";
  cargarInsumos(e.target.value);
});

cargarInsumos();
cargarPreciosLeche();
