"""
Serveur HTTP intégré UniShare – communication multi-utilisateurs sur le réseau local.
Démarre sur 0.0.0.0:8765 en thread daemon au lancement de l'application.
Les autres instances se connectent via l'IP affichée dans Paramètres > Réseau.
"""
import json
import threading
import socket
import time as _time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import utils.data as data_module

_server_instance = None
_server_port     = 8765


class UniShareHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silencieux

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        n = int(self.headers.get("Content-Length", 0))
        if n > 0:
            try:
                return json.loads(self.rfile.read(n).decode("utf-8"))
            except Exception:
                return {}
        return {}

    # ── OPTIONS (CORS preflight) ──────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── GET ───────────────────────────────────────────────────────────────────

    def do_GET(self):
        parsed  = urlparse(self.path)
        path    = parsed.path
        params  = parse_qs(parsed.query)

        if path == "/ping":
            self._send_json({"status": "ok", "server": "UniShare"})

        elif path == "/users":
            users = [
                {k: v for k, v in u.items() if k != "password_hash"}
                for u in data_module.REGISTERED_USERS.values()
            ]
            self._send_json(users)

        elif path == "/posts":
            self._send_json(data_module.POSTS)

        elif path == "/messages":
            conv_id = params.get("conv_id", [""])[0]
            msgs = getattr(data_module, "ALL_MESSAGES", [])
            if conv_id:
                msgs = [m for m in msgs if m.get("conv_id") == conv_id]
            self._send_json(msgs)

        else:
            self._send_json({"error": "not found"}, 404)

    # ── POST ──────────────────────────────────────────────────────────────────

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/register":
            email = body.get("email", "")
            if not email:
                self._send_json({"error": "email required"}, 400)
                return
            data_module.REGISTERED_USERS[email] = body
            data_module.save_users()
            self._send_json({"ok": True})

        elif path == "/posts":
            body.setdefault("id", str(int(_time.time() * 1000)))
            existing_ids = {p.get("id") for p in data_module.POSTS}
            if body["id"] not in existing_ids:
                data_module.POSTS.insert(0, body)
                data_module.save_posts()
            self._send_json({"ok": True, "id": body["id"]})

        elif path == "/posts/like":
            post_id = body.get("post_id")
            user_id = body.get("user_id", "anon")
            for post in data_module.POSTS:
                if post.get("id") == post_id:
                    liked_by = post.setdefault("liked_by", [])
                    if user_id in liked_by:
                        liked_by.remove(user_id)
                        post["likes"] = max(0, post.get("likes", 1) - 1)
                    else:
                        liked_by.append(user_id)
                        post["likes"] = post.get("likes", 0) + 1
                    data_module.save_posts()
                    break
            self._send_json({"ok": True})

        elif path == "/posts/comment":
            post_id = body.get("post_id")
            comment = body.get("comment", {})
            for post in data_module.POSTS:
                if post.get("id") == post_id:
                    post.setdefault("comments", []).append(comment)
                    data_module.save_posts()
                    break
            self._send_json({"ok": True})

        elif path == "/messages":
            if not hasattr(data_module, "ALL_MESSAGES"):
                data_module.ALL_MESSAGES = []
            body.setdefault("id",   str(int(_time.time() * 1000)))
            body.setdefault("time", _time.strftime("%H:%M"))
            data_module.ALL_MESSAGES.append(body)
            data_module.save_messages()
            self._send_json({"ok": True})

        else:
            self._send_json({"error": "not found"}, 404)


# ── Public API ────────────────────────────────────────────────────────────────

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def start_server(port=8765):
    global _server_instance, _server_port
    _server_port = port
    try:
        _server_instance = HTTPServer(("0.0.0.0", port), UniShareHandler)
        t = threading.Thread(target=_server_instance.serve_forever, daemon=True)
        t.start()
        return True, get_local_ip(), port
    except OSError:
        return False, get_local_ip(), port


def is_running():
    return _server_instance is not None
