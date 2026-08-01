"use strict";

const colors = {
  requirement: "#fb7185", decision: "#f59e0b", issue: "#f97316", evidence: "#c084fc",
  review: "#e879f9", memory: "#a78bfa", session: "#818cf8",
  file: "#22d3ee", config: "#38bdf8", document: "#60a5fa",
  symbol: "#8b5cf6", test: "#34d399", coverage: "#2dd4bf",
  "test-result": "#10b981", "delivery-issue": "#fb923c",
  "pull-request": "#facc15", commit: "#94a3b8"
};
const kindOrder = ["requirement", "decision", "issue", "delivery-issue", "pull-request", "evidence", "review", "memory", "session", "file", "config", "document", "symbol", "test", "coverage", "test-result", "commit"];
const proofKinds = new Set(["test", "evidence", "coverage", "test-result", "commit", "pull-request"]);
const pathLimits = { depth: 6, visited: 800, results: 6 };
const renderLimits = { nodes: 240, edges: 900, focusDepth: 2, relationships: 80 };
const state = {
  data: null, report: null, review: null, nodeById: new Map(), edgeByNode: new Map(),
  degreeById: new Map(), searchIndex: [], pathAdjacency: new Map(), enabled: new Set(),
  nodes: [], edges: [], visibleNodeById: new Map(), selected: null, viewMode: "overview",
  focus: null, scale: 1, tx: 0, ty: 0, alpha: 1, frame: null
};
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
  const [response, reviewResponse, reportResponse] = await Promise.all([
    fetch("/graph.json", { cache: "no-store" }),
    fetch("/review.json", { cache: "no-store" }),
    fetch("/change-report.json", { cache: "no-store" })
  ]);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  state.data = await response.json();
  if (reviewResponse.ok) {
    state.review = await reviewResponse.json();
    state.report = state.review.change_report;
  } else if (reportResponse.ok) state.report = await reportResponse.json();
  state.nodeById = new Map(state.data.nodes.map(node => [node.id, node]));
  buildGraphIndexes();
  state.pathAdjacency = buildPathAdjacency();
  for (const node of state.data.nodes) state.enabled.add(node.kind);
  renderFilters(); renderChangeReport(); rebuild(); bindEvents(); fitGraph();
}

function buildGraphIndexes() {
  state.edgeByNode = new Map(); state.degreeById = new Map();
  for (const node of state.data.nodes) {
    state.edgeByNode.set(node.id, []); state.degreeById.set(node.id, 0);
  }
  for (const edge of state.data.edges) {
    if (!state.nodeById.has(edge.source) || !state.nodeById.has(edge.target)) continue;
    state.edgeByNode.get(edge.source).push(edge);
    state.edgeByNode.get(edge.target).push(edge);
    state.degreeById.set(edge.source, state.degreeById.get(edge.source) + 1);
    state.degreeById.set(edge.target, state.degreeById.get(edge.target) + 1);
  }
  for (const edges of state.edgeByNode.values()) edges.sort(compareEdges);
  state.searchIndex = state.data.nodes.map(node => ({
    node,
    text: `${node.id} ${node.label} ${node.path || ""} ${node.kind}`.toLowerCase()
  }));
}

function renderChangeReport() {
  if (!state.report) return;
  const report = state.report;
  const toggle = document.querySelector("#report-toggle");
  toggle.hidden = false;
  if (state.review) {
    toggle.textContent = "Revision review";
    document.querySelector("#report-title").textContent = "Revision review";
  }
  const summary = [
    reportDatum("strategy", report.test_strategy.replaceAll("-", " ")),
    reportDatum("analysis", report.analysis_state),
    reportDatum("coverage", report.analysis_coverage_complete ? "complete" : "fallback required")
  ];
  if (state.review) {
    summary.push(reportDatum("mode", state.review.mode));
    summary.push(reportDatum("base", shortRevision(state.review.base_revision)));
    summary.push(reportDatum("head", shortRevision(state.review.head_revision)));
  }
  document.querySelector("#report-summary").innerHTML = summary.join("");
  renderReportItems("#report-requirements", report.requirements, item => ({
    id: item.requirement.id,
    label: item.requirement.label,
    score: item.score,
    confidence: item.confidence
  }));
  renderReportItems("#report-tests", report.tests, item => ({
    id: item.test.id,
    label: item.test.path || item.test.label,
    score: item.score,
    confidence: item.confidence
  }));
  renderOutcomeEvidence();
}

function renderOutcomeEvidence() {
  const section = document.querySelector("#report-outcomes");
  const comparison = state.review && state.review.test_outcomes;
  if (!comparison) return;
  section.hidden = false;
  document.querySelector("#report-outcome-summary").innerHTML = [
    reportDatum("freshness", comparison.freshness),
    reportDatum("commit", shortRevision(comparison.outcome_commit)),
    reportDatum("executed", comparison.test_count)
  ].join("");
  document.querySelector("#report-outcome-tests").innerHTML = comparison.tests.length
    ? comparison.tests.map(item => `<div class="report-item report-observation"><strong>${escapeHTML(item.path)}</strong><small>${escapeHTML(item.status)}${item.duration_ms === undefined ? "" : ` · ${item.duration_ms} ms`}</small></div>`).join("")
    : "<p class='hint'>No test path was recorded for this execution.</p>";
  const evidence = document.querySelector("#report-outcome-comparison");
  if (comparison.freshness !== "aligned") {
    evidence.innerHTML = "<p class='path-note'>Comparison withheld because the outcome commit is stale.</p>";
    return;
  }
  evidence.innerHTML = [
    outcomePaths("Selected and executed", comparison.predicted_and_executed),
    outcomePaths("Selected, not executed", comparison.predicted_not_executed),
    outcomePaths("Executed, not selected", comparison.executed_not_predicted)
  ].join("");
}

function outcomePaths(label, paths) {
  const value = paths.length ? paths.join(", ") : "none";
  return `<div class="outcome-paths"><strong>${escapeHTML(label)}</strong><span>${escapeHTML(value)}</span></div>`;
}

function shortRevision(value) { return String(value || "").slice(0, 12); }

function reportDatum(label, value) {
  return `<div class="report-datum"><span>${escapeHTML(label)}</span><strong>${escapeHTML(String(value))}</strong></div>`;
}

function renderReportItems(selector, items, valueOf) {
  const container = document.querySelector(selector);
  container.innerHTML = items.length ? items.map(item => {
    const value = valueOf(item);
    return `<button class="report-item" data-node="${escapeAttr(value.id)}"><strong>${escapeHTML(value.label)}</strong><small>${escapeHTML(value.confidence)} · ${value.score}/100</small></button>`;
  }).join("") : "<p class='hint'>No ranked items at this confidence threshold.</p>";
  for (const button of container.querySelectorAll(".report-item")) bindFocusButton(button);
}

function renderStats() {
  const stats = document.querySelector("#stats");
  stats.innerHTML = stat(state.data.nodes.length, "total nodes")
    + stat(state.data.edges.length, "total links")
    + stat(state.nodes.length, "shown nodes")
    + stat(state.edges.length, "shown links");
  const hiddenNodes = Math.max(0, state.data.nodes.length - state.nodes.length);
  const mode = state.viewMode === "focus" ? "Focused neighborhood" : "Ranked overview";
  document.querySelector("#window-status").textContent = hiddenNodes
    ? `${mode}; ${hiddenNodes} nodes remain available through global search and linked navigation.`
    : `${mode}; every enabled node is visible.`;
  document.querySelector("#overview").disabled = state.viewMode === "overview";
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
    label.className = "filter"; label.dataset.kind = kind;
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
  const rawNodes = state.viewMode === "focus" ? focusedNodes() : overviewNodes();
  const ids = new Set(rawNodes.map(node => node.id));
  const width = stage.clientWidth || 900, height = stage.clientHeight || 600;
  state.nodes = rawNodes.map((raw, index) => {
    const old = prior.get(raw.id); if (old) return { ...raw, x: old.x, y: old.y, vx: old.vx, vy: old.vy };
    const angle = seeded(raw.id) * Math.PI * 2;
    const radius = 80 + (index % 11) * 13;
    return { ...raw, x: width / 2 + Math.cos(angle) * radius, y: height / 2 + Math.sin(angle) * radius, vx: 0, vy: 0 };
  });
  state.visibleNodeById = new Map(state.nodes.map(node => [node.id, node]));
  state.edges = windowEdges(ids);
  document.querySelector("#empty").hidden = state.nodes.length > 0;
  draw(); renderStats(); state.alpha = 1; tick(); applySearch();
}

function overviewNodes() {
  const enabled = state.data.nodes.filter(node => state.enabled.has(node.kind));
  if (enabled.length <= renderLimits.nodes) return enabled;
  const groups = new Map();
  for (const node of enabled) {
    if (!groups.has(node.kind)) groups.set(node.kind, []);
    groups.get(node.kind).push(node);
  }
  const orderedGroups = [...groups.entries()]
    .sort((a, b) => kindPriority(a[0]) - kindPriority(b[0]) || a[0].localeCompare(b[0]))
    .map(([, nodes]) => nodes.sort(compareOverviewNodes));
  const selected = [];
  let offset = 0;
  while (selected.length < renderLimits.nodes) {
    let added = false;
    for (const nodes of orderedGroups) {
      if (offset >= nodes.length) continue;
      selected.push(nodes[offset]); added = true;
      if (selected.length >= renderLimits.nodes) break;
    }
    if (!added) break;
    offset += 1;
  }
  return selected;
}

function focusedNodes() {
  const target = state.nodeById.get(state.focus);
  if (!target || !state.enabled.has(target.kind)) return [];
  const included = new Map([[target.id, target]]);
  let frontier = [target.id];
  for (let depth = 0; depth < renderLimits.focusDepth && frontier.length; depth++) {
    const next = [];
    for (const id of frontier) {
      for (const edge of state.edgeByNode.get(id) || []) {
        const neighborId = edge.source === id ? edge.target : edge.source;
        const neighbor = state.nodeById.get(neighborId);
        if (!neighbor || included.has(neighborId) || !state.enabled.has(neighbor.kind)) continue;
        included.set(neighborId, neighbor); next.push(neighborId);
        if (included.size >= renderLimits.nodes) break;
      }
      if (included.size >= renderLimits.nodes) break;
    }
    frontier = next.sort();
    if (included.size >= renderLimits.nodes) break;
  }
  return [...included.values()];
}

function windowEdges(ids) {
  const values = new Map();
  for (const id of ids) {
    for (const edge of state.edgeByNode.get(id) || []) {
      if (!ids.has(edge.source) || !ids.has(edge.target)) continue;
      values.set(edgeKey(edge), edge);
    }
  }
  return [...values.values()].sort(compareWindowEdges).slice(0, renderLimits.edges);
}

function compareWindowEdges(a, b) {
  const aFocus = state.viewMode === "focus" && (a.source === state.focus || a.target === state.focus);
  const bFocus = state.viewMode === "focus" && (b.source === state.focus || b.target === state.focus);
  return Number(bFocus) - Number(aFocus) || compareEdges(a, b);
}

function compareOverviewNodes(a, b) {
  return (state.degreeById.get(b.id) || 0) - (state.degreeById.get(a.id) || 0)
    || a.id.localeCompare(b.id);
}

function kindPriority(kind) {
  const index = kindOrder.indexOf(kind);
  return index < 0 ? kindOrder.length : index;
}

function draw() {
  edgeLayer.innerHTML = ""; nodeLayer.innerHTML = "";
  for (const edge of state.edges) {
    const line = svgElement("line"); line.dataset.source = edge.source; line.dataset.target = edge.target;
    line.dataset.relation = edge.relation; edgeLayer.append(line);
  }
  for (const node of state.nodes) {
    const group = svgElement("g"); group.classList.add("node"); group.dataset.id = node.id;
    group.setAttribute("role", "button"); group.setAttribute("tabindex", "0");
    group.setAttribute("aria-label", `${node.label} · ${node.kind}`);
    const circle = svgElement("circle"); circle.setAttribute("r", String(radius(node)));
    circle.setAttribute("fill", color(node.kind));
    const label = svgElement("text"); label.setAttribute("x", String(radius(node) + 5)); label.setAttribute("y", "3");
    label.textContent = shortLabel(node.label); label.hidden = degree(node.id) < 2 && state.nodes.length > 80;
    const title = svgElement("title"); title.textContent = `${node.label} · ${node.kind}`;
    group.append(circle, label, title); bindNode(group, node); nodeLayer.append(group);
  }
  updatePositions();
}

function tick() {
  if (!state.nodes.length) return;
  const width = stage.clientWidth, height = stage.clientHeight;
  const byId = state.visibleNodeById;
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
  const byId = state.visibleNodeById;
  for (const line of edgeLayer.children) {
    const a = byId.get(line.dataset.source), b = byId.get(line.dataset.target); if (!a || !b) continue;
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y); line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
  }
  for (const group of nodeLayer.children) {
    const node = byId.get(group.dataset.id); if (node) group.setAttribute("transform", `translate(${node.x} ${node.y})`);
  }
}

function bindNode(group, node) {
  let moved = false, dragOrigin = null;
  group.addEventListener("pointerdown", event => {
    event.stopPropagation(); moved = false; dragOrigin = { x: event.clientX, y: event.clientY };
    node.fixed = true; group.setPointerCapture(event.pointerId);
  });
  group.addEventListener("pointermove", event => {
    if (!group.hasPointerCapture(event.pointerId)) return;
    if (dragOrigin && Math.hypot(event.clientX - dragOrigin.x, event.clientY - dragOrigin.y) >= 4) moved = true;
    const point = graphPoint(event); node.x = point.x; node.y = point.y; node.vx = 0; node.vy = 0; updatePositions();
  });
  group.addEventListener("pointerup", event => {
    if (group.hasPointerCapture(event.pointerId)) group.releasePointerCapture(event.pointerId);
    if (!moved) selectNode(node.id);
    dragOrigin = null;
    node.fixed = false; state.alpha = Math.max(state.alpha, .15); tick();
  });
  group.addEventListener("pointercancel", () => { dragOrigin = null; node.fixed = false; });
  group.addEventListener("click", () => { if (!moved) selectNode(node.id); });
  group.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectNode(node.id); }
  });
}

function bindEvents() {
  search.addEventListener("input", applySearch);
  search.addEventListener("keydown", event => {
    if (event.key !== "Enter") return;
    const match = bestSearchMatch(search.value);
    if (match) { event.preventDefault(); focusNode(match.id); }
  });
  document.addEventListener("keydown", event => {
    if (event.key === "/" && document.activeElement !== search) { event.preventDefault(); search.focus(); }
    if (event.key === "Escape") { closeDetail(); closeChangeReport(); }
  });
  document.querySelector("#fit").addEventListener("click", fitGraph);
  document.querySelector("#overview").addEventListener("click", showOverview);
  document.querySelector("#focus-neighborhood").addEventListener("click", () => {
    if (state.selected) showFocusedWindow(state.selected);
  });
  document.querySelector("#close-detail").addEventListener("click", closeDetail);
  document.querySelector("#report-toggle").addEventListener("click", openChangeReport);
  document.querySelector("#close-report").addEventListener("click", closeChangeReport);
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
    const node = state.visibleNodeById.get(group.dataset.id);
    const haystack = `${node.id} ${node.label} ${node.path || ""} ${node.kind}`.toLowerCase();
    group.classList.toggle("dim", Boolean(query) && !haystack.includes(query));
    const text = group.querySelector("text"); if (query && haystack.includes(query)) text.hidden = false;
  }
}

function bestSearchMatch(value) {
  const query = value.trim().toLowerCase();
  if (!query) return null;
  let partial = null;
  for (const entry of state.searchIndex) {
    const node = entry.node;
    if (
      node.id.toLowerCase() === query
      || node.label.toLowerCase() === query
      || (node.path || "").toLowerCase() === query
    ) return node;
    if (!partial && entry.text.includes(query)) partial = node;
  }
  return partial;
}

function selectNode(id) {
  const node = state.visibleNodeById.get(id); if (!node) return;
  state.selected = id;
  for (const group of nodeLayer.children) group.classList.toggle("selected", group.dataset.id === id);
  for (const line of edgeLayer.children) line.classList.toggle("active", line.dataset.source === id || line.dataset.target === id);
  document.querySelector("#detail-kind").textContent = node.kind;
  document.querySelector("#detail-title").textContent = node.label;
  document.querySelector("#detail-id").textContent = node.id;
  const metadata = { ...(node.path ? { path: node.path } : {}), ...node.metadata };
  document.querySelector("#detail-meta").innerHTML = Object.entries(metadata).map(([key, value]) => `<div class="meta-row"><span>${escapeHTML(key.replaceAll("_", " "))}</span><span>${escapeHTML(typeof value === "object" ? JSON.stringify(value) : String(value))}</span></div>`).join("");
  renderEvidencePaths(node);
  const connected = state.edgeByNode.get(id) || [];
  const shownRelationships = connected.slice(0, renderLimits.relationships);
  const omitted = connected.length - shownRelationships.length;
  document.querySelector("#detail-links").innerHTML = connected.length ? shownRelationships.map(edge => {
    const outgoing = edge.source === id, otherId = outgoing ? edge.target : edge.source;
    const other = state.nodeById.get(otherId);
    const relation = outgoing ? edge.relation : (edge.inverse || edge.relation);
    const detail = [edge.category, edge.evidence].filter(Boolean).join(" · ");
    return `<button class="relationship" data-node="${escapeAttr(otherId)}"><b>${outgoing ? "→" : "←"} ${escapeHTML(relation)}</b> ${escapeHTML(other?.label || otherId)}<small>${escapeHTML(detail)}</small></button>`;
  }).join("") + (omitted > 0 ? `<p class="path-note">${omitted} additional relationships are omitted from this bounded detail view.</p>` : "") : "<p class='hint'>No relationships yet.</p>";
  for (const button of document.querySelectorAll(".relationship")) bindFocusButton(button);
  document.querySelector("#detail").classList.add("open");
}

function renderEvidencePaths(node) {
  const container = document.querySelector("#detail-paths");
  const paths = findEvidencePaths(node.id);
  container.innerHTML = paths.length ? paths.map((path, index) => {
    const destination = path.destination;
    const hops = path.hops.map(hop => `${hop.direction} ${hop.relation} ${hop.label}`).join(" · ");
    return `<button class="evidence-path" data-path="${index}" data-node="${escapeAttr(destination.id)}"><strong>${escapeHTML(destination.kind)} · ${escapeHTML(destination.label)}</strong><small>${escapeHTML(hops)}</small></button>`;
  }).join("") : "<p class='hint'>No bounded evidence path found.</p>";
  for (const button of container.querySelectorAll(".evidence-path")) bindFocusButton(button);
}

function bindFocusButton(button) {
  const activate = () => focusNode(button.dataset.node);
  button.addEventListener("click", activate);
  button.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); activate(); }
  });
}

function findEvidencePaths(startId) {
  const nodes = state.nodeById;
  const adjacency = state.pathAdjacency;
  const visited = new Set([startId]);
  const queue = [{ id: startId, hops: [] }];
  const results = [];
  while (queue.length && visited.size <= pathLimits.visited && results.length < pathLimits.results) {
    const current = queue.shift();
    if (current.hops.length >= pathLimits.depth) continue;
    for (const hop of adjacency.get(current.id) || []) {
      if (visited.has(hop.id) || visited.size >= pathLimits.visited) continue;
      visited.add(hop.id);
      const hops = [...current.hops, hop];
      const destination = nodes.get(hop.id);
      if (proofKinds.has(destination.kind)) results.push({ destination, hops });
      if (results.length >= pathLimits.results) break;
      queue.push({ id: hop.id, hops });
    }
  }
  return results;
}

function buildPathAdjacency() {
  const nodes = state.nodeById;
  const adjacency = new Map();
  const add = (source, hop) => {
    if (!adjacency.has(source)) adjacency.set(source, []);
    adjacency.get(source).push(hop);
  };
  for (const edge of state.data.edges) {
    const target = nodes.get(edge.target), source = nodes.get(edge.source);
    if (!target || !source) continue;
    add(edge.source, { id: edge.target, label: target.label, relation: edge.relation, direction: "→" });
    add(edge.target, { id: edge.source, label: source.label, relation: edge.inverse || edge.relation, direction: "←" });
  }
  for (const hops of adjacency.values()) {
    hops.sort((a, b) => a.id.localeCompare(b.id) || a.relation.localeCompare(b.relation) || a.direction.localeCompare(b.direction));
  }
  return adjacency;
}

function focusNode(id) {
  closeChangeReport();
  const globalNode = state.nodeById.get(id); if (!globalNode) return;
  if (!state.enabled.has(globalNode.kind)) {
    state.enabled.add(globalNode.kind); syncFilter(globalNode.kind);
  }
  const node = state.visibleNodeById.get(id);
  if (!node) { showFocusedWindow(id); return; }
  state.scale = Math.max(state.scale, 1.2); state.tx = stage.clientWidth * .54 - node.x * state.scale; state.ty = stage.clientHeight * .5 - node.y * state.scale; transform(); selectNode(id);
}

function showFocusedWindow(id) {
  if (!state.nodeById.has(id)) return;
  state.viewMode = "focus"; state.focus = id; rebuild(); fitGraph();
  const node = state.visibleNodeById.get(id);
  if (node) selectNode(id);
}

function showOverview() {
  closeDetail(); search.value = ""; state.viewMode = "overview"; state.focus = null; rebuild(); fitGraph();
}

function syncFilter(kind) {
  const label = [...document.querySelectorAll(".filter")].find(item => item.dataset.kind === kind);
  if (!label) return;
  label.querySelector("input").checked = true; label.classList.remove("off");
}
function closeDetail() { document.querySelector("#detail").classList.remove("open"); state.selected = null; for (const item of document.querySelectorAll(".selected,.active")) item.classList.remove("selected", "active"); }
function openChangeReport() { closeDetail(); document.querySelector("#change-report").classList.add("open"); }
function closeChangeReport() { document.querySelector("#change-report").classList.remove("open"); }

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
function degree(id) { return state.degreeById.get(id) || 0; }
function radius(node) { return 5.2 + Math.min(8, Math.sqrt(degree(node.id)) * 1.55) + (node.kind === "requirement" || node.kind === "decision" ? 2 : 0); }
function color(kind) { return colors[kind] || "#a3a3a3"; }
function seeded(value) { let hash = 2166136261; for (const char of value) { hash ^= char.charCodeAt(0); hash = Math.imul(hash, 16777619); } return (hash >>> 0) / 4294967295; }
function shortLabel(label) { return label.length > 44 ? `${label.slice(0, 41)}…` : label; }
function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
function svgElement(name) { return document.createElementNS("http://www.w3.org/2000/svg", name); }
function escapeHTML(value) { const span = document.createElement("span"); span.textContent = value; return span.innerHTML; }
function escapeAttr(value) { return escapeHTML(value).replaceAll('"', "&quot;"); }
function edgeKey(edge) { return `${edge.source}\u0000${edge.target}\u0000${edge.relation}\u0000${edge.evidence}`; }
function compareEdges(a, b) { return edgeKey(a).localeCompare(edgeKey(b)); }
