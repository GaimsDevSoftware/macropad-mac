#!/usr/bin/env python3
"""
Makropad — konfigurator med grafisk grensesnitt.

Start:  .venv/bin/python app.py
Åpner http://127.0.0.1:8777 i nettleseren.
"""
import http.server
import json
import os
import socketserver
import threading
import webbrowser

import device
import xzkj

PORT = 8777
HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, "bindings.json")


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"layer": 1, "bindings": {}}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def parse_spec(spec: str):
    """'cmd+c' | 'h,e,i' | 'mouse:left' -> ('kbd', entries) | ('mouse', mask)"""
    spec = str(spec).strip().lower()
    if not spec:
        return None
    if spec.startswith("mouse:"):
        btn = {"left": 1, "right": 2, "middle": 4}.get(spec[6:])
        if btn is None:
            raise ValueError(f"Ukjent museknapp: {spec[6:]}")
        return ("mouse", btn)
    entries = []
    for chord in spec.split(","):
        chord = chord.strip()
        delay = 0
        if "@" in chord:
            chord, d = chord.rsplit("@", 1)
            delay = int(d)
        parts = [p.strip() for p in chord.split("+")]
        for m in parts[:-1]:
            if m not in xzkj.MODIFIERS:
                raise ValueError(f"Ukjent modifikator: {m}")
            entries.append((0, xzkj.MODIFIERS[m]))
        key = parts[-1]
        if key in xzkj.MODIFIERS:
            entries.append((delay, xzkj.MODIFIERS[key]))
        elif key in xzkj.HID_CODES:
            entries.append((delay, xzkj.HID_CODES[key]))
        else:
            raise ValueError(f"Ukjent tast: {key}")
    if not 1 <= len(entries) <= 18:
        raise ValueError(f"{len(entries)} trykk — maks 18")
    return ("kbd", entries)


def flash(state):
    parsed = []
    for target, spec in state["bindings"].items():
        p = parse_spec(spec)
        if p:
            parsed.append((device.resolve(target), p))
    if not parsed:
        return 0
    h = xzkj.open_vendor_interface()
    try:
        for key_id, (kind, val) in parsed:
            if kind == "kbd":
                xzkj.bind_key_sequence(h, key_id, val, state.get("layer", 1))
            else:
                xzkj.bind_mouse_click(h, key_id, val, state.get("layer", 1))
        xzkj.finish(h)
    finally:
        h.close()
    return len(parsed)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "ui.html"), "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/state":
            st = load_state()
            st["keys"] = sorted(xzkj.HID_CODES)
            st["mods"] = sorted(set(xzkj.MODIFIERS))
            self._json(st)
        elif self.path == "/api/device":
            try:
                h = xzkj.open_vendor_interface()
                h.close()
                self._json({"connected": True})
            except Exception as e:
                self._json({"connected": False, "error": str(e)})
        else:
            self.send_error(404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or "{}")
        if self.path == "/api/save":
            save_state(data)
            self._json({"ok": True})
        elif self.path == "/api/flash":
            save_state(data)
            try:
                count = flash(data)
                self._json({"ok": True, "count": count})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, 200)
        elif self.path == "/api/validate":
            try:
                parse_spec(data.get("spec", ""))
                self._json({"ok": True})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
        else:
            self.send_error(404)


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        print(f"Makropad-konfigurator kjører på {url}  (Ctrl+C for å avslutte)")
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nAvsluttet.")
