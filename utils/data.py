import os
import sys
import json
import time as _time

# ─── Chemins de persistance ───────────────────────────────────────────────────
# Fonctionne en développement ET en .exe PyInstaller
if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR      = os.path.join(_BASE, "data")
USERS_FILE    = os.path.join(DATA_DIR, "users.json")
POSTS_FILE    = os.path.join(DATA_DIR, "posts.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

os.makedirs(DATA_DIR, exist_ok=True)

FAKE_USERS = []
FAKE_POSTS = []

# ─── État global ──────────────────────────────────────────────────────────────
REGISTERED_USERS = {}   # { email: user_dict }
CURRENT_USER     = None
SAVED_FOR_LATER  = []
NOTIFICATIONS    = []
POSTS            = []   # posts persistés
ALL_MESSAGES     = []   # messages de chat persistés
FOLLOW_REQUESTS  = {}   # { from_uid: {name, avatar, ...} } — demandes reçues par l'utilisateur courant
FOLLOWS          = {"followers": {}, "following": {}}


# ─── Persistance JSON ─────────────────────────────────────────────────────────

def load_all_data():
    """Charge users, posts et messages depuis les fichiers JSON au démarrage."""
    global REGISTERED_USERS, POSTS, ALL_MESSAGES

    # Utilisateurs inscrits
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                REGISTERED_USERS = json.load(f)
        except Exception:
            REGISTERED_USERS = {}

    # Posts persistés
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                POSTS = json.load(f)
        except Exception:
            POSTS = []
    else:
        POSTS = []

    # Messages
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
                ALL_MESSAGES = json.load(f)
        except Exception:
            ALL_MESSAGES = []
    else:
        ALL_MESSAGES = []


def save_users():
    """Sauvegarde REGISTERED_USERS dans users.json."""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(REGISTERED_USERS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def save_posts():
    """Sauvegarde POSTS dans posts.json."""
    try:
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(POSTS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def save_messages():
    """Sauvegarde ALL_MESSAGES dans messages.json."""
    try:
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(ALL_MESSAGES, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_all_swipe_users(current_user_id=None):
    """Retourne les utilisateurs réels inscrits pour le swipe (hors utilisateur courant)."""
    users = []
    for email, u in REGISTERED_USERS.items():
        if u.get("id") == current_user_id:
            continue
        users.append({
            "id":           u.get("id", email),
            "name":         u.get("name", ""),
            "age":          u.get("age", 20),
            "school":       u.get("school", ""),
            "major":        u.get("major", ""),
            "avatar":       u.get("avatar", "👤"),
            "avatar_color": u.get("avatar_color", "#1565C0"),
            "photo_path":   u.get("photo_path"),
            "bio":          u.get("bio", ""),
            "posts":        u.get("posts", []),
            "badges":       u.get("badges", ["🎓 Nouveau"]),
        })
    return users


def add_notification(text, kind="info"):
    NOTIFICATIONS.append({"type": kind, "text": text, "read": False,
                           "time": _time.strftime("%H:%M")})


# ─── Paramètres globaux de l'application ─────────────────────────────────────
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
APP_SETTINGS = {
    "language":        "Français",   # Français | English | العربية
    "notifications":   True,
    "account_private": False,
}


def load_settings():
    global APP_SETTINGS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                APP_SETTINGS.update(json.load(f))
        except Exception:
            pass


def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(APP_SETTINGS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ─── Chargement au démarrage ──────────────────────────────────────────────────
load_all_data()
load_settings()
