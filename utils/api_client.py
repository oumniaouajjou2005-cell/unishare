"""
Client UniShare – Firebase (online) + serveur local (LAN) + JSON (offline).
Priorité : Firebase si configuré → serveur local → JSON local.
"""
import urllib.request
import json
import time as _time

_SERVER_URL = "http://127.0.0.1:8765"
_TIMEOUT    = 3


def set_server_url(url: str):
    global _SERVER_URL
    _SERVER_URL = url.rstrip("/")


def get_server_url() -> str:
    return _SERVER_URL


# ── Firebase lazy import ──────────────────────────────────────────────────────

def _fb():
    from utils import firebase_client
    return firebase_client


# ── Primitives LAN ────────────────────────────────────────────────────────────

def _get(path: str):
    try:
        with urllib.request.urlopen(f"{_SERVER_URL}{path}", timeout=_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _post(path: str, data: dict):
    try:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req  = urllib.request.Request(
            f"{_SERVER_URL}{path}", data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST")
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


# ── Ping ──────────────────────────────────────────────────────────────────────

def ping() -> bool:
    fb = _fb()
    if fb.is_configured():
        return fb.db_get("_ping") is not None
    try:
        with urllib.request.urlopen(f"{_SERVER_URL}/ping", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


# ── Utilisateurs ──────────────────────────────────────────────────────────────

def fetch_users():
    fb = _fb()
    if fb.is_configured():
        data = fb.db_get("users") or {}
        if isinstance(data, dict):
            return list(data.values())
        return []
    return _get("/users") or []


def register_user(user: dict):
    fb = _fb()
    if fb.is_configured():
        email = user.get("email", "")
        if not email:
            return None
        key   = fb.encode_email(email)
        clean = {k: v for k, v in user.items() if k != "password_hash"}
        return fb.db_set(f"users/{key}", clean)
    return _post("/register", user)


def update_user_profile(user: dict):
    fb = _fb()
    if fb.is_configured():
        email = user.get("email", "")
        if not email:
            return None
        key   = fb.encode_email(email)
        clean = {k: v for k, v in user.items() if k != "password_hash"}
        return fb.db_patch(f"users/{key}", clean)
    return _post("/register", user)


def fetch_user_profile(email: str):
    fb = _fb()
    if fb.is_configured():
        key = fb.encode_email(email)
        return fb.db_get(f"users/{key}")
    return None


# ── Publications ──────────────────────────────────────────────────────────────

def fetch_posts():
    fb = _fb()
    if fb.is_configured():
        data = fb.db_get("posts") or {}
        if isinstance(data, dict) and data:
            posts = list(data.values())
            posts.sort(key=lambda p: p.get("timestamp", 0), reverse=True)
            return posts
        return []
    return _get("/posts")


def push_post(post: dict):
    fb = _fb()
    if fb.is_configured():
        post.setdefault("timestamp", int(_time.time() * 1000))
        post_id = post.get("id", str(int(_time.time() * 1000)))
        post["id"] = post_id
        return fb.db_set(f"posts/{post_id}", post)
    return _post("/posts", post)


def delete_post(post_id: str):
    fb = _fb()
    if fb.is_configured():
        return fb.db_delete(f"posts/{post_id}")
    return None


def like_post(post_id: str, user_id: str):
    fb = _fb()
    if fb.is_configured():
        post = fb.db_get(f"posts/{post_id}")
        if post:
            liked_by = post.get("liked_by") or {}
            if isinstance(liked_by, list):
                liked_by = {u: True for u in liked_by}
            if user_id in liked_by:
                del liked_by[user_id]
                likes = max(0, post.get("likes", 1) - 1)
            else:
                liked_by[user_id] = True
                likes = post.get("likes", 0) + 1
            fb.db_patch(f"posts/{post_id}", {"likes": likes, "liked_by": liked_by})
        return True
    return _post("/posts/like", {"post_id": post_id, "user_id": user_id})


def add_comment(post_id: str, comment: dict):
    fb = _fb()
    if fb.is_configured():
        comment.setdefault("id", str(int(_time.time() * 1000)))
        fb.db_push(f"posts/{post_id}/comments", comment)
        return True
    return _post("/posts/comment", {"post_id": post_id, "comment": comment})


# ── Messages ──────────────────────────────────────────────────────────────────

def fetch_messages(conv_id: str):
    fb = _fb()
    if fb.is_configured():
        data = fb.db_get(f"messages/{conv_id}") or {}
        if isinstance(data, dict) and data:
            msgs = list(data.values())
            msgs.sort(key=lambda m: m.get("id", "0"))
            return msgs
        return []
    return _get(f"/messages?conv_id={conv_id}")


def send_message(msg: dict):
    fb = _fb()
    if fb.is_configured():
        msg_id  = msg.get("id", str(int(_time.time() * 1000)))
        conv_id = msg.get("conv_id", "unknown")
        msg["id"] = msg_id
        return fb.db_set(f"messages/{conv_id}/{msg_id}", msg)
    return _post("/messages", msg)


# ── Follow system ─────────────────────────────────────────────────────────────

def send_follow_request(from_user: dict, to_user_id: str):
    """Envoie une demande de suivi à to_user_id."""
    fb = _fb()
    if not fb.is_configured():
        return False
    from_id = from_user.get("id", "")
    if not from_id or not to_user_id:
        return False
    request = {
        "from_id":     from_id,
        "from_name":   from_user.get("name", ""),
        "from_avatar": from_user.get("avatar", "👤"),
        "from_color":  from_user.get("avatar_color", "#1565C0"),
        "from_school": from_user.get("school", ""),
        "timestamp":   int(_time.time() * 1000),
    }
    return fb.db_set(f"follow_requests/{to_user_id}/{from_id}", request)


def get_follow_requests(user_id: str):
    """Récupère les demandes de suivi reçues par user_id."""
    fb = _fb()
    if not fb.is_configured():
        return {}
    data = fb.db_get(f"follow_requests/{user_id}") or {}
    return data if isinstance(data, dict) else {}


def accept_follow(from_uid: str, to_uid: str):
    """Accepte une demande de suivi."""
    fb = _fb()
    if not fb.is_configured():
        return False
    # Ajouter dans les deux sens
    fb.db_set(f"follows/{to_uid}/followers/{from_uid}", True)
    fb.db_set(f"follows/{from_uid}/following/{to_uid}", True)
    # Supprimer la demande
    fb.db_delete(f"follow_requests/{to_uid}/{from_uid}")
    return True


def reject_follow(from_uid: str, to_uid: str):
    """Refuse une demande de suivi."""
    fb = _fb()
    if not fb.is_configured():
        return False
    fb.db_delete(f"follow_requests/{to_uid}/{from_uid}")
    return True


def get_followers_count(user_id: str) -> int:
    fb = _fb()
    if not fb.is_configured():
        return 0
    data = fb.db_get(f"follows/{user_id}/followers") or {}
    return len(data) if isinstance(data, dict) else 0


def get_following_count(user_id: str) -> int:
    fb = _fb()
    if not fb.is_configured():
        return 0
    data = fb.db_get(f"follows/{user_id}/following") or {}
    return len(data) if isinstance(data, dict) else 0
