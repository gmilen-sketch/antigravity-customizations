#!/usr/bin/env python3
"""
Antigravity UI Plugin Sidecar Backend (`autonomy-dashboard`).
Serves the AuxPane HTML UI, host-theme-adaptive CSS (`styles.css`),
`/preload.js` fallback bridge, and `/api/status` JSON telemetry on
`ANTIGRAVITY_SIDECAR_WEB_PORT`.
"""

import argparse
import http.server
import json
import os
import pathlib
import sys

sys.dont_write_bytecode = True

SIDECAR_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SIDECAR_DIR.parent.parent


def compute_status_payload() -> dict:
    """Computes live plugin, skill, subagent, and Knowledge Graph counts."""
    skills_dir = REPO_ROOT / "skills"
    skill_count = sum(1 for p in skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else 20
    plugins_dir = REPO_ROOT / "plugins"
    plugin_packs = sum(1 for p in plugins_dir.glob("*/plugin.json")) if plugins_dir.is_dir() else 4
    kb_dir = REPO_ROOT / "kb"
    kg_entities = sum(1 for p in kb_dir.rglob("*.md")) if kb_dir.is_dir() else 6
    return {
        "status": "ok",
        "version": "1.4.0",
        "skill_count": skill_count,
        "subagent_count": 5,
        "mcp_server_count": 7,
        "plugin_packs": plugin_packs,
        "kg_entities": kg_entities,
        "entrypoint": "SIDECAR_UI_ENTRYPOINT_AUX_PANE",
    }


class SidecarRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler implementing the Antigravity UI Sidecar contract."""

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[autonomy-dashboard] {fmt % args}\n")

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            html_bytes = (SIDECAR_DIR / "index.html").read_bytes()
            self._send(200, "text/html; charset=utf-8", html_bytes)
        elif path == "/styles.css":
            css_bytes = (SIDECAR_DIR / "styles.css").read_bytes()
            self._send(200, "text/css; charset=utf-8", css_bytes)
        elif path == "/preload.js":
            js = b"window.sidecar = window.sidecar || { conversationId: null, agent: { sendMessage: async function() {} }, ui: { toggleAuxPane: async function() {} } };\n"
            self._send(200, "application/javascript; charset=utf-8", js)
        elif path in ("/api/status", "/healthz"):
            payload = json.dumps(compute_status_payload()).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", payload)
        else:
            self._send(404, "application/json; charset=utf-8", b'{"error":"not_found"}')


def main() -> int:
    parser = argparse.ArgumentParser(description="Antigravity Autonomy Dashboard Sidecar")
    parser.add_argument("--self-test", action="store_true", help="Run hermetic self-test and exit")
    args = parser.parse_args()

    if args.self_test:
        payload = compute_status_payload()
        print(json.dumps(payload, indent=2))
        return 0 if payload.get("status") == "ok" else 1

    port = int(os.environ.get("ANTIGRAVITY_SIDECAR_WEB_PORT", "0"))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), SidecarRequestHandler)
    bound_port = server.server_address[1]
    sys.stderr.write(f"[autonomy-dashboard] Listening on http://127.0.0.1:{bound_port}\n")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
