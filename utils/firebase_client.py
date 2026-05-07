"""
Client Firebase REST pour UniShare.
Utilise l'API REST Firebase (pas de bibliothèque externe requise).
- Firebase Authentication (Email/Password)
- Firebase Realtime Database
"""
import json
import os
import sys
import urllib.request
import urllib.error
import time as _time

# ── Chemin de configuration ────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_FILE = os.path.join(_BASE, "data", "firebase_config.json")

FIREBASE_CONFIG = {
    "apiKey":        "",
    "projectId":     "",
    "databaseURL":   "",
    "storageBucket": "",
}

_ID_TOKEN      = None
_REFRESH_TOKEN = None
_UID           = None
_TOKEN_EXPIRY  = 0
_TIMEOUT       = 8


def load_config():
    """Recharge la config depuis firebase_config.json."""
    global FIREBASE_CONFIG
    if os.path.exists(_CONFIG_FILE):
        try:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                FIREBASE_CONFIG.update(data)
        except Exception:
            pass


def is_configured() -> bool:
    return bool(FIREBASE_CONFIG.get("apiKey") and FIREBASE_CONFIG.get("databaseURL"))


def get_uid() -> str:
    return _UID or ""


# ── Helpers internes ──────────────────────────────────────────────────────────

def _db_url(path: str) -> str:
    base = FIREBASE_CONFIG["databaseURL"].rstrip("/")
    url  = f"{base}/{path}.json"
    if _ID_TOKEN:
        url += f"?auth={_ID_TOKEN}"
    return url


def _request(method: str, url: str, data=None):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    req  = urllib.request.Request(url, data=body, method=method)
    if body:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            print(f"[Firebase] HTTP {e.code}: {err}")
        except Exception:
            pass
        return None
    except Exception as ex:
        print(f"[Firebase] Erreur réseau: {ex}")
        return None


# ── Authentification ──────────────────────────────────────────────────────────

def sign_up(email: str, password: str):
    """Crée un compte Firebase Auth. Retourne le résultat ou None."""
    global _ID_TOKEN, _REFRESH_TOKEN, _UID, _TOKEN_EXPIRY
    url = (f"https://identitytoolkit.googleapis.com/v1/accounts:signUp"
           f"?key={FIREBASE_CONFIG['apiKey']}")
    r = _request("POST", url, {
        "email": email, "password": password, "returnSecureToken": True
    })
    if r and "idToken" in r:
        _ID_TOKEN      = r["idToken"]
        _REFRESH_TOKEN = r.get("refreshToken", "")
        _UID           = r.get("localId", "")
        _TOKEN_EXPIRY  = _time.time() + int(r.get("expiresIn", 3600))
        return r
    return None


def sign_in(email: str, password: str):
    """Connecte un utilisateur Firebase. Retourne le résultat ou None."""
    global _ID_TOKEN, _REFRESH_TOKEN, _UID, _TOKEN_EXPIRY
    url = (f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
           f"?key={FIREBASE_CONFIG['apiKey']}")
    r = _request("POST", url, {
        "email": email, "password": password, "returnSecureToken": True
    })
    if r and "idToken" in r:
        _ID_TOKEN      = r["idToken"]
        _REFRESH_TOKEN = r.get("refreshToken", "")
        _UID           = r.get("localId", "")
        _TOKEN_EXPIRY  = _time.time() + int(r.get("expiresIn", 3600))
        return r
    return None


def refresh_token():
    """Renouvelle le token si expiré."""
    global _ID_TOKEN, _TOKEN_EXPIRY
    if not _REFRESH_TOKEN:
        return False
    url = (f"https://securetoken.googleapis.com/v1/token"
           f"?key={FIREBASE_CONFIG['apiKey']}")
    r = _request("POST", url, {
        "grant_type": "refresh_token", "refresh_token": _REFRESH_TOKEN
    })
    if r and "id_token" in r:
        _ID_TOKEN     = r["id_token"]
        _TOKEN_EXPIRY = _time.time() + int(r.get("expires_in", 3600))
        return True
    return False


def send_email_verification():
    """Envoie un email de vérification à l'utilisateur connecté."""
    if not _ID_TOKEN:
        return False
    url = (f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
           f"?key={FIREBASE_CONFIG['apiKey']}")
    r = _request("POST", url, {"requestType": "VERIFY_EMAIL", "idToken": _ID_TOKEN})
    return r is not None


def is_email_verified() -> bool:
    """Vérifie si l'email de l'utilisateur connecté est vérifié."""
    if not _ID_TOKEN:
        return False
    url = (f"https://identitytoolkit.googleapis.com/v1/accounts:lookup"
           f"?key={FIREBASE_CONFIG['apiKey']}")
    r = _request("POST", url, {"idToken": _ID_TOKEN})
    if r and "users" in r and r["users"]:
        return r["users"][0].get("emailVerified", False)
    return False


def ensure_token():
    """S'assure que le token est valide (le renouvelle si nécessaire)."""
    if _TOKEN_EXPIRY and _time.time() > _TOKEN_EXPIRY - 60:
        refresh_token()


def logout():
    global _ID_TOKEN, _REFRESH_TOKEN, _UID, _TOKEN_EXPIRY
    _ID_TOKEN = _REFRESH_TOKEN = _UID = None
    _TOKEN_EXPIRY = 0


# ── Encodage clé email ────────────────────────────────────────────────────────

def encode_email(email: str) -> str:
    """Firebase n'accepte pas '.' dans les clés → encode l'email."""
    return email.lower().replace(".", ",").replace("@", "__at__")


def decode_email(key: str) -> str:
    return key.replace("__at__", "@").replace(",", ".")


# ── Database CRUD ─────────────────────────────────────────────────────────────

def db_get(path: str):
    ensure_token()
    return _request("GET", _db_url(path))


def db_set(path: str, data):
    ensure_token()
    return _request("PUT", _db_url(path), data)


def db_push(path: str, data):
    ensure_token()
    return _request("POST", _db_url(path), data)


def db_patch(path: str, data):
    ensure_token()
    return _request("PATCH", _db_url(path), data)


def db_delete(path: str):
    ensure_token()
    return _request("DELETE", _db_url(path))


# ── Session persistante ───────────────────────────────────────────────────────
_SESSION_FILE = os.path.join(_BASE, "data", "session.json")


def save_session(user_data: dict):
    """Sauvegarde la session (token + données user) pour auto-connexion."""
    try:
        session = {
            "refresh_token": _REFRESH_TOKEN or "",
            "uid":           _UID or "",
            "user_data":     {k: v for k, v in user_data.items() if k != "password_hash"},
        }
        with open(_SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_session():
    """Charge la session sauvegardée et renouvelle le token. Retourne user_data ou None."""
    global _ID_TOKEN, _REFRESH_TOKEN, _UID, _TOKEN_EXPIRY
    if not os.path.exists(_SESSION_FILE):
        return None
    try:
        with open(_SESSION_FILE, "r", encoding="utf-8") as f:
            session = json.load(f)
        rt = session.get("refresh_token", "")
        if not rt:
            return None
        _REFRESH_TOKEN = rt
        _UID = session.get("uid", "")
        if refresh_token():
            return session.get("user_data")
        return None
    except Exception:
        return None


def clear_session():
    """Supprime la session sauvegardée (déconnexion)."""
    try:
        if os.path.exists(_SESSION_FILE):
            os.remove(_SESSION_FILE)
    except Exception:
        pass


# ── Chargement initial ────────────────────────────────────────────────────────
load_config()
