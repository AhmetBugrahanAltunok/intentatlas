from __future__ import annotations

import hashlib
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from socketserver import TCPServer
from urllib.parse import parse_qs, urlsplit

from .graph import MAX_GRAPH_DOCUMENT_BYTES, AtlasGraph
from .graph_query import GraphQuerySnapshot
from .safe_io import read_bounded_regular_file

CONTENT_TYPES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
}


class LoopbackHTTPServer(ThreadingHTTPServer):
    def server_bind(self) -> None:
        TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = str(host)
        self.server_port = int(port)


def serve_graph(
    graph_path: Path | None,
    *,
    host: str = "127.0.0.1",
    port: int = 4317,
    open_browser: bool = True,
    graph_document: bytes | None = None,
    change_report_document: bytes | None = None,
    review_document: bytes | None = None,
) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("The viewer may only bind to the IPv4 loopback address")
    if isinstance(port, bool) or not isinstance(port, int) or port < 0 or port > 65535:
        raise ValueError("Port must be between 0 and 65535")
    bind_host = "127.0.0.1" if host == "localhost" else host
    served_graph_document: bytes
    if graph_document is None:
        if graph_path is None or not graph_path.is_file():
            raise ValueError(f"Graph not found: {graph_path}. Run `intentatlas scan` first.")
        loaded = read_bounded_regular_file(
            graph_path, MAX_GRAPH_DOCUMENT_BYTES
        )
        if loaded is None:
            raise ValueError(
                "Cannot read viewer graph as a stable regular file within the "
                f"{MAX_GRAPH_DOCUMENT_BYTES}-byte limit"
            )
        served_graph_document = loaded
    else:
        if len(graph_document) > MAX_GRAPH_DOCUMENT_BYTES:
            raise ValueError(
                f"Viewer graph exceeds the {MAX_GRAPH_DOCUMENT_BYTES}-byte limit"
            )
        served_graph_document = graph_document
    try:
        graph_value = json.loads(served_graph_document.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot parse viewer graph: {exc}") from exc
    graph = AtlasGraph.from_dict(graph_value, source="viewer graph")
    snapshot = GraphQuerySnapshot(
        graph,
        hashlib.sha256(served_graph_document).hexdigest(),
    )

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            host_header = self.headers.get("Host")
            if host_header is None or host_header.casefold() not in allowed_hosts:
                self.send_error(421, "Unexpected Host header")
                return
            parsed = urlsplit(self.path)
            route = parsed.path
            if route.startswith("/api/graph/"):
                self._graph_query(route, parse_qs(parsed.query, keep_blank_values=True))
                return
            if route == "/api/report/change" and change_report_document is not None:
                self._send(change_report_document, "application/json; charset=utf-8")
                return
            if route == "/api/report/review" and review_document is not None:
                self._send(review_document, "application/json; charset=utf-8")
                return
            if route == "/graph.json":
                self._send(served_graph_document, "application/json; charset=utf-8")
                return
            if route == "/change-report.json" and change_report_document is not None:
                self._send(change_report_document, "application/json; charset=utf-8")
                return
            if route == "/review.json" and review_document is not None:
                self._send(review_document, "application/json; charset=utf-8")
                return
            asset = CONTENT_TYPES.get(route)
            if asset is None:
                self.send_error(404)
                return
            name, content_type = asset
            body = files("intentatlas.web").joinpath(name).read_bytes()
            self._send(body, content_type)

        def _graph_query(self, route: str, query: dict[str, list[str]]) -> None:
            try:
                if route == "/api/graph/overview":
                    value = snapshot.overview(
                        node_limit=_query_int(query, "node_limit", 240),
                        edge_limit=_query_int(query, "edge_limit", 900),
                    )
                elif route == "/api/graph/search":
                    value = snapshot.search(
                        _query_text(query, "q"),
                        limit=_query_int(query, "limit", 20),
                    )
                elif route == "/api/graph/neighborhood":
                    value = snapshot.neighborhood(
                        _query_text(query, "id"),
                        depth=_query_int(query, "depth", 2),
                        node_limit=_query_int(query, "node_limit", 240),
                        edge_limit=_query_int(query, "edge_limit", 900),
                    )
                elif route == "/api/graph/paths":
                    target = query.get("target", [None])[0]
                    value = snapshot.paths(
                        _query_text(query, "start"),
                        target=target,
                        depth=_query_int(query, "depth", 6),
                        visited_limit=_query_int(query, "visited_limit", 800),
                        result_limit=_query_int(query, "result_limit", 6),
                    )
                else:
                    self.send_error(404)
                    return
            except ValueError as exc:
                body = json.dumps(
                    {"schema_version": 1, "error": str(exc)}, sort_keys=True
                ).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            body = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
            self._send(body, "application/json; charset=utf-8")

        def _send(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")

            self.end_headers()
            self.wfile.write(body)

        def end_headers(self) -> None:
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                "script-src 'self'; connect-src 'self'; base-uri 'none'; "
                "form-action 'none'; frame-ancestors 'none'",
            )
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            super().end_headers()

        def log_message(self, format: str, *args: object) -> None:
            return

    server = LoopbackHTTPServer((bind_host, port), Handler)
    actual_port = server.server_address[1]
    allowed_host_names = {bind_host}
    if host == "localhost":
        allowed_host_names.add("localhost")
    allowed_hosts = {
        value
        for allowed_host in allowed_host_names
        for value in (allowed_host, f"{allowed_host}:{actual_port}")
    }
    url = f"http://{bind_host}:{actual_port}"
    print(f"IntentAtlas viewer: {url}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    if open_browser:
        threading.Timer(0.2, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _query_text(query: dict[str, list[str]], name: str) -> str:
    values = query.get(name, [])
    if len(values) != 1:
        raise ValueError(f"{name} must appear exactly once")
    return values[0]


def _query_int(query: dict[str, list[str]], name: str, default: int) -> int:
    values = query.get(name)
    if values is None:
        return default
    if len(values) != 1 or not values[0].isascii() or not values[0].isdigit():
        raise ValueError(f"{name} must be an integer")
    return int(values[0])
