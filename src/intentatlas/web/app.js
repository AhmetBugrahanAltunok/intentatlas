"use strict";

const colors = {
  requirement: "#fb7185", decision: "#f59e0b", evidence: "#c084fc",
  review: "#e879f9", memory: "#a78bfa", session: "#818cf8",
  file: "#22d3ee", config: "#38bdf8", document: "#60a5fa",
  symbol: "#8b5cf6", test: "#34d399", commit: "#94a3b8"
};
const kindOrder = ["requirement", "decision", "evidence", "review", "memory", "session", "file", "config", "document", "symbol", "test", "commit"];
const state = { data: null, enabled: new Set(), nodes: [], edges: [], selected: null, scale: 1, tx: 0, ty: 0, alpha: 1, frame: null };
const svg = document.querySelector("#graph");
const viewport = document.querySelector("#viewport");
const edgeLayer = document.querySelector("#edges");
const nodeLayer = document.querySelector("#nodes");
const stage = document.querySelector("#stage");
const search = document.querySelector("#search");

boot().catch(error => {
  document.querySelector("#empty").hidden = false;
  document.querySelector("#empty").textContent = `Could not load graph: ${error.message}`;
});

async function boot() {
  const response = await fetch("/graph.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  state.data = await response.json();
  for (const node of state.data.nodes) state.enabled.add(node.kind);
  renderStats(); renderFilters(); rebuild(); bindEvents(); fitGraph();
}

function renderStats() {
  const stats = document.querySelector("#stats");
  stats.innerHTML = stat(state.data.nodes.length, "nodes") + stat(state.data.edges.length, "links");
}
function stat(value, label) { return `<div class="stat"><strong>${value}</strong><span>${label}</span></div>`; }

function renderFilters() {
  const counts = new Map();
  for (const node of state.data.nodes) counts.set(node.kind, (counts.get(node.kind) || 0) + 1);
  const kinds = [...counts.keys()].sort((a, b) => {
    const ai = kindOrder.indexOf(a), bi = kindOrder.indexOf(b);
    return (ai < 0 ? 99 : ai) - (bi < 0 ? 99 : bi) || a.localeCompare(b);
  });
  const filters = document.querySelector("#filters");
  filters.innerHTML = "";
  for (const kind of kinds) {
    const label = document.createElement("label");
    label.className = "filter";
    label.innerHTML = `<input type="checkbox" checked><span class="swatch" style="color:${color(kind)};background:${color(kind)}"></span><span>${escapeHTML(kind)}</span><span class="count">${counts.get(kind)}</span>`;
    const input = label.querySelector("input");
    input.addEventListener("change", () => {
      input.checked ? state.enabled.add(kind) : state.enabled.delete(kind);
      label.classList.toggle("off", !input.checked); rebuild();
    });
    filters.append(label);
  }
}

function rebuild() {
  if (state.frame) cancelAnimationFrame(state.frame);
  const prior = new Map(state.nodes.map(node => [node.id, node]));
  const rawNodes = state.data.nodes.filter(node => state.enabled.has(node.kind));
  const ids = new Set(rawNodes.map(node => node.id));
  const width = stage.clientWidth || 900, height = stage.clientHeight || 600;
  state.nodes = rawNodes.map((raw, index) => {
    const old = prior.get(raw.id); if (old) return { ...raw, x: old.x, y: old.y, vx: old.vx, vy: old.vy };
    const angle = seeded(raw.id) * Math.PI * 2;
    const radius = 80 + (index % 11) * 13;
    return { ...raw, x: width / 2 + Math.cos(angle) * radius, y: height / 2 + Math.sin(angle) * radius, vx: 0, vy: 0 };
  });
  state.edges = state.data.edges.filter(edge => ids.has(edge.source) && ids.has(edge.target));
  document.querySelector("#empty").hidden = state.nodes.length > 0;
  draw(); state.alpha = 1; tick(); applySearch();
}

function draw() {
  const byId = new Map(state.nodes.map(node => [node.id, node]));
  edgeLayer.innerHTML = ""; nodeLayer.innerHTML = "";
  for (const edge of state.edges) {
    const line = svgElement("line"); line.dataset.source = edge.source; line.dataset.target = edge.target;
    line.dataset.relation = edge.relation; edgeLayer.append(line);
  }
  for (const node of state.nodes) {
    const group = svgElement("g"); group.classList.add("node"); group.dataset.id = node.id;
    group.setAttribute("role", "button"); group.setAttribute("tabindex", "0");
    group.setAttribute("aria-label", `${node.label} · ${node.kind}`);
    const circle = svgElement("circle"); circle.setAttribute("r", String(radius(node, byId)));
    circle.setAttribute("fill", color(node.kind));
    const label = svgElement("text"); label.setAttribute("x", String(radius(node, byId) + 5)); label.setAttribute("y", "3");
    label.textContent = shortLabel(node.label); label.hidden = degree(node.id) < 2 && state.nodes.length > 80;
    const title = svgElement("title"); title.textContent = `${node.label} · ${node.kind}`;
    group.append(circle, label, title); bindNode(group, node); nodeLayer.append(group);
  }
  updatePositions();
}

function tick() {
  if (!state.nodes.length) return;
  const width = stage.clientWidth, height = stage.clientHeight;
  const byId = new Map(state.nodes.map(node => [node.id, node]));
  const alpha = state.alpha;
  for (const edge of state.edges) {
    const a = byId.get(edge.source), b = byId.get(edge.target); if (!a || !b) continue;
    const dx = b.x - a.x, dy = b.y - a.y, distance = Math.hypot(dx, dy) || 1;
    const force = (distance - 92) * .008 * alpha;
    const fx = dx / distance * force, fy = dy / distance * force;
    a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy;
  }
  const limit = Math.min(state.nodes.length, 320);
  for (let i = 0; i < limit; i++) for (let j = i + 1; j < limit; j++) {
    const a = state.nodes[i], b = state.nodes[j]; let dx = b.x - a.x, dy = b.y - a.y;
    let squared = dx * dx + dy * dy; if (squared < 1) { dx = .5; dy = .5; squared = .5; }
    const force = Math.min(2.2, 950 / squared) * alpha;
    a.vx -= dx * force; a.vy -= dy * force; b.vx += dx * force; b.vy += dy * force;
  }
  for (const node of state.nodes) {
    if (node.fixed) continue;
    node.vx += (width / 2 - node.x) * .0009 * alpha;
    node.vy += (height / 2 - node.y) * .0009 * alpha;
    node.vx *= .84; node.vy *= .84; node.x += node.vx; node.y += node.vy;
  }
  updatePositions(); state.alpha *= .982;
  if (state.alpha > .018) state.frame = requestAnimationFrame(tick);
}

function updatePositions() {
  const byId = new Map(state.nodes.map(node => [node.id, node]));
  for (const line of edgeLayer.children) {
    const a = byId.get(line.dataset.source), b = byId.get(line.dataset.target); if (!a || !b) continue;
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y); line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
  }
  for (const group of nodeLayer.children) {
    const node = byId.get(group.dataset.id); if (node) group.setAttribute("transform", `translate(${node.x} ${node.y})`);
  }
}

function bindNode(group, node) {
  let moved = false;
  group.addEventListener("pointerdown", event => {
    event.stopPropagation(); moved = false; node.fixed = true; group.setPointerCapture(event.pointerId);
  });
  group.addEventListener("pointermove", event => {
    if (!group.hasPointerCapture(event.pointerId)) return; moved = true;
    const point = graphPoint(event); node.x = point.x; node.y = point.y; node.vx = 0; node.vy = 0; updatePositions();
  });
  group.addEventListener("pointerup", event => {
    if (group.hasPointerCapture(event.pointerId)) group.releasePointerCapture(event.pointerId);
    node.fixed = false; state.alpha = Math.max(state.alpha, .15); tick();
  });
  group.addEventListener("click", () => { if (!moved) selectNode(node.id); });
  group.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectNode(node.id); }
  });
}

function bindEvents() {
  search.addEventListener("input", applySearch);
  document.addEventListener("keydown", event => {
    if (event.key === "/" && document.activeElement !== search) { event.preventDefault(); search.focus(); }
    if (event.key === "Escape") closeDetail();
  });
  document.querySelector("#fit").addEventListener("click", fitGraph);
  document.querySelector("#close-detail").addEventListener("click", closeDetail);
  let pan = null;
  svg.addEventListener("pointerdown", event => {
    if (event.target.closest(".node")) return;
    pan = { x: event.clientX, y: event.clientY, tx: state.tx, ty: state.ty };
    svg.setPointerCapture(event.pointerId); stage.classList.add("panning");
  });
  svg.addEventListener("pointermove", event => {
    if (!pan) return; state.tx = pan.tx + event.clientX - pan.x; state.ty = pan.ty + event.clientY - pan.y; transform();
  });
  svg.addEventListener("pointerup", event => { pan = null; stage.classList.remove("panning"); if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId); });
  svg.addEventListener("wheel", event => {
    event.preventDefault(); const next = clamp(state.scale * Math.exp(-event.deltaY * .0012), .18, 4);
    const rect = svg.getBoundingClientRect(), x = event.clientX - rect.left, y = event.clientY - rect.top;
    state.tx = x - (x - state.tx) * next / state.scale; state.ty = y - (y - state.ty) * next / state.scale; state.scale = next; transform();
  }, { passive: false });
  window.addEventListener("resize", fitGraph);
}

function applySearch() {
  const query = search.value.trim().toLowerCase();
  for (const group of nodeLayer.children) {
    const node = state.nodes.find(item => item.id === group.dataset.id);
    const haystack = `${node.id} ${node.label} ${node.path || ""} ${node.kind}`.toLowerCase();
    group.classList.toggle("dim", Boolean(query) && !haystack.includes(query));
    const text = group.querySelector("text"); if (query && haystack.includes(query)) text.hidden = false;
  }
}

function selectNode(id) {
  const node = state.nodes.find(item => item.id === id); if (!node) return;
  state.selected = id;
  for (const group of nodeLayer.children) group.classList.toggle("selected", group.dataset.id === id);
  for (const line of edgeLayer.children) line.classList.toggle("active", line.dataset.source === id || line.dataset.target === id);
  document.querySelector("#detail-kind").textContent = node.kind;
  document.querySelector("#detail-title").textContent = node.label;
  document.querySelector("#detail-id").textContent = node.id;
  const metadata = { ...(node.path ? { path: node.path } : {}), ...node.metadata };
  document.querySelector("#detail-meta").innerHTML = Object.entries(metadata).map(([key, value]) => `<div class="meta-row"><span>${escapeHTML(key.replaceAll("_", " "))}</span><span>${escapeHTML(typeof value === "object" ? JSON.stringify(value) : String(value))}</span></div>`).join("");
  const connected = state.data.edges.filter(edge => edge.source === id || edge.target === id);
  document.querySelector("#detail-links").innerHTML = connected.length ? connected.map(edge => {
    const outgoing = edge.source === id, otherId = outgoing ? edge.target : edge.source;
    const other = state.data.nodes.find(item => item.id === otherId);
    return `<button class="relationship" data-node="${escapeAttr(otherId)}"><b>${outgoing ? "→" : "←"} ${escapeHTML(edge.relation)}</b> ${escapeHTML(other?.label || otherId)}<small>${escapeHTML(edge.evidence)}</small></button>`;
  }).join("") : "<p class='hint'>No relationships yet.</p>";
  for (const button of document.querySelectorAll(".relationship")) button.addEventListener("click", () => focusNode(button.dataset.node));
  document.querySelector("#detail").classList.add("open");
}

function focusNode(id) {
  const node = state.nodes.find(item => item.id === id);
  if (!node) { search.value = id; applySearch(); return; }
  state.scale = Math.max(state.scale, 1.2); state.tx = stage.clientWidth * .54 - node.x * state.scale; state.ty = stage.clientHeight * .5 - node.y * state.scale; transform(); selectNode(id);
}
function closeDetail() { document.querySelector("#detail").classList.remove("open"); state.selected = null; for (const item of document.querySelectorAll(".selected,.active")) item.classList.remove("selected", "active"); }

function fitGraph() {
  if (!state.nodes.length) return;
  const xs = state.nodes.map(node => node.x), ys = state.nodes.map(node => node.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const width = Math.max(100, maxX - minX), height = Math.max(100, maxY - minY), pad = 90;
  state.scale = clamp(Math.min((stage.clientWidth - pad) / width, (stage.clientHeight - pad) / height), .22, 1.6);
  state.tx = stage.clientWidth / 2 - (minX + maxX) / 2 * state.scale; state.ty = stage.clientHeight / 2 - (minY + maxY) / 2 * state.scale; transform();
}
function transform() { viewport.setAttribute("transform", `translate(${state.tx} ${state.ty}) scale(${state.scale})`); }
function graphPoint(event) { const rect = svg.getBoundingClientRect(); return { x: (event.clientX - rect.left - state.tx) / state.scale, y: (event.clientY - rect.top - state.ty) / state.scale }; }
function degree(id) { return state.edges.reduce((sum, edge) => sum + Number(edge.source === id || edge.target === id), 0); }
function radius(node) { return 5.2 + Math.min(8, Math.sqrt(degree(node.id)) * 1.55) + (node.kind === "requirement" || node.kind === "decision" ? 2 : 0); }
function color(kind) { return colors[kind] || "#a3a3a3"; }
function seeded(value) { let hash = 2166136261; for (const char of value) { hash ^= char.charCodeAt(0); hash = Math.imul(hash, 16777619); } return (hash >>> 0) / 4294967295; }
function shortLabel(label) { return label.length > 44 ? `${label.slice(0, 41)}…` : label; }
function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
function svgElement(name) { return document.createElementNS("http://www.w3.org/2000/svg", name); }
function escapeHTML(value) { const span = document.createElement("span"); span.textContent = value; return span.innerHTML; }
function escapeAttr(value) { return escapeHTML(value).replaceAll('"', "&quot;"); }
