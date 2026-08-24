"""Localhost HTTP server wrapping aicalc.serve.api (stdlib only).

Error contract (the loud-failure rules, HTTP-shaped):
  CaseError / UnknownName          -> 400 (bad input; message carries the
                                          JSON-path and did-you-mean text)
  NeedsManualFact family,
  UnsupportedFlags                 -> 422 (valid input the engine refuses to
                                          guess about; hint names the fix)
  anything else                    -> 500 (never swallowed)
"""
from __future__ import annotations

import json
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from ..calc import (AmbiguousRandomDamage, NeedsManualFact, NeedsPartyData,
                    NeedsWeightData)
from ..case_loader import CaseError
from ..names import UnknownName
from ..scoring import UnsupportedFlags
from . import api

STATIC = Path(__file__).resolve().parent / "static"

MIME = {".html": "text/html; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".json": "application/json",
        ".png": "image/png", ".svg": "image/svg+xml"}

_HINTS = {
    AmbiguousRandomDamage: ("add a damage.moves override (or "
                            "damage.best_damaging_move) for the named move"),
    NeedsPartyData: "set damage.party_member_outdamages in the battle doc",
    NeedsWeightData: "set the Pokemon's weight_hg or add a damage override",
    UnsupportedFlags: "remove the unsupported flag(s) from battle.flags",
}


def _error_body(exc: Exception) -> dict:
    body = {"error": {"type": type(exc).__name__, "message": str(exc)}}
    for etype, hint in _HINTS.items():
        if isinstance(exc, etype):
            body["error"]["hint"] = hint
            break
    return body


class Handler(BaseHTTPRequestHandler):
    server_version = "aicalc-serve"

    def log_message(self, fmt, *args):  # quieter default logging
        pass

    # --- plumbing -----------------------------------------------------------

    def _send_json(self, obj: dict, status: int = 200) -> None:
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CaseError(f"request body is not valid JSON: {exc}") from None

    def _handle(self, fn) -> None:
        try:
            self._send_json(fn())
        except (CaseError, UnknownName) as exc:
            self._send_json(_error_body(exc), 400)
        except (NeedsManualFact, UnsupportedFlags) as exc:
            self._send_json(_error_body(exc), 422)
        except Exception as exc:  # noqa: BLE001 -- surfaced, never swallowed
            traceback.print_exc()
            self._send_json(_error_body(exc), 500)

    def _serve_static(self, path: str) -> None:
        name = path.lstrip("/") or "index.html"
        target = (STATIC / name).resolve()
        if not target.is_file() or STATIC not in target.parents and target != STATIC:
            self.send_error(404)
            return
        payload = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type",
                         MIME.get(target.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    # --- routes -------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        url = urlparse(self.path)
        if url.path == "/api/meta":
            self._handle(api.meta)
        elif url.path == "/api/trainers":
            self._handle(api.trainers)
        elif url.path == "/api/trainer":
            query = parse_qs(url.query)
            try:
                tr_id = int(query.get("id", ["x"])[0])
            except ValueError:
                self._send_json({"error": {"type": "CaseError",
                                           "message": "id must be an integer"}}, 400)
                return
            self._handle(lambda: api.trainer(tr_id))
        elif url.path == "/api/tables":
            self._handle(api.tables)
        else:
            self._serve_static(url.path)

    def do_POST(self) -> None:  # noqa: N802
        url = urlparse(self.path)
        if url.path == "/api/probabilities":
            body = self._read_json_safe()
            if body is not None:
                self._handle(lambda: api.probabilities(body))
        else:
            self.send_error(404)

    def _read_json_safe(self) -> dict | None:
        try:
            return self._read_json()
        except CaseError as exc:
            self._send_json(_error_body(exc), 400)
            return None


def serve(port: int = 8573) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
