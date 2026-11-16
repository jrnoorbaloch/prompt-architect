"""Local web UI server (stdlib only). Run: prompt-architect ui"""
from __future__ import annotations

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

from .engine import engineer
from .providers import DEFAULT_MODELS, ProviderError


def _ui_html() -> bytes:
    return resources.files("prompt_architect").joinpath("ui/index.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str = "application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, _ui_html(), "text/html; charset=utf-8")
        elif self.path == "/api/models":
            self._send(200, json.dumps(DEFAULT_MODELS).encode())
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        if self.path != "/api/engineer":
            return self._send(404, b'{"error":"not found"}')
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            res = engineer(
                body.get("prompt", ""),
                provider=body.get("provider", "anthropic"),
                model=body.get("model") or None,
                api_key=body.get("api_key") or None,
                base_url=body.get("base_url") or None,
                target_model=body.get("target_model") or "any LLM",
                mode=body.get("mode", "standard"),
                prompt_language=body.get("prompt_language") or "English",
                extra_context=body.get("extra_context", ""),
            )
            self._send(200, json.dumps(res.to_dict()).encode())
        except (ProviderError, ValueError) as e:
            self._send(400, json.dumps({"error": str(e)}).encode())
        except Exception as e:  # noqa: BLE001
            self._send(500, json.dumps({"error": f"{type(e).__name__}: {e}"}).encode())


def serve(host: str = "127.0.0.1", port: int = 7860, open_browser: bool = True):
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print(f"✨ Prompt Architect UI running at {url}  (Ctrl+C to stop)")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nBye!")
