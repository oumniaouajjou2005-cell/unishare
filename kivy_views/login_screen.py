import hashlib
import time
import random
import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assests", "logo_unishare.png",
)

DARK_BLU = "#0D47A1"
PINK     = "#1976D2"
MID_BLU  = "#1565C0"
GOLD     = "#FFB300"
GREEN    = "#2E7D32"
DARK     = "#212121"
GRAY     = "#90A4AE"

SCHOOLS = [
    "ENCG Casablanca", "ENCG Agadir", "ENCG Fès", "ENCG Marrakech",
    "ISCAE Rabat", "ISCAE Casablanca", "HEM Casablanca", "Mundiapolis",
    "FSJES Casablanca", "FSJES Rabat", "FSJES Tanger", "FSJES Marrakech",
    "EMI Rabat", "ENSAM Casablanca", "INPT Rabat", "ENSET Mohammedia",
    "INSEA Rabat", "EST Casablanca", "EST Rabat", "ENSA Marrakech",
    "Université Hassan II", "Université Mohammed V", "Autre",
]
MAJORS = [
    "Finance", "Marketing", "GRH", "Audit & Contrôle", "Informatique de Gestion",
    "Génie Informatique", "Génie Civil", "Génie Électrique", "Statistiques",
    "Droit des Affaires", "Économie", "Management", "Autre",
]
AVATARS = ["👩‍💼", "👩‍🎓", "👩‍💻", "👨‍💼", "👨‍🎓", "👨‍💻", "👨‍🔬", "👩‍🔬"]
COLORS  = ["#9C27B0", "#E91E63", "#009688", "#1565C0", "#F57C00", "#2E7D32",
           "#6A1B9A", "#AD1457", "#00695C", "#0D47A1", "#E65100", "#1B5E20"]


def _c(h):
    return get_color_from_hex(h)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# ── Popup d'erreur / info ─────────────────────────────────────────────────────
def _popup(title, msg):
    box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
    box.add_widget(MDLabel(
        text=msg, halign="center",
        theme_text_color="Custom", text_color=_c(DARK),
        size_hint_y=None, height=dp(80),
    ))
    btn = MDRaisedButton(
        text="OK", size_hint=(1, None), height=dp(44),
        md_bg_color=_c(PINK),
    )
    box.add_widget(btn)
    p = Popup(title=title, content=box,
              size_hint=(0.85, None), height=dp(200))
    btn.bind(on_release=p.dismiss)
    p.open()


# ── Bannière avec gradient bleu ───────────────────────────────────────────────
class Banner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.size_hint_y = None
        self.height = dp(210)
        self.padding = [dp(20), dp(16)]
        self.spacing = dp(4)
        self.bind(size=self._draw, pos=self._draw)

        if os.path.exists(LOGO_PATH):
            row = BoxLayout(size_hint_y=None, height=dp(100))
            row.add_widget(Widget())
            row.add_widget(Image(
                source=LOGO_PATH,
                size_hint=(None, None), size=(dp(96), dp(96)),
                allow_stretch=True, keep_ratio=True,
            ))
            row.add_widget(Widget())
            self.add_widget(row)
        else:
            self.add_widget(MDLabel(
                text="🎓", font_style="H3", halign="center",
                theme_text_color="Custom", text_color=(1, 1, 1, 1),
                size_hint_y=None, height=dp(80),
            ))

        self.add_widget(MDLabel(
            text="UniShare",
            font_style="H5", halign="center", bold=True,
            theme_text_color="Custom", text_color=(1, 1, 1, 1),
            size_hint_y=None, height=dp(34),
        ))
        self.add_widget(MDLabel(
            text="Le savoir partagé · La réussite assurée",
            font_style="Caption", halign="center",
            theme_text_color="Custom", text_color=_c(GOLD),
            size_hint_y=None, height=dp(22),
        ))

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            c1, c2 = _c(DARK_BLU), _c(PINK)
            steps = 20
            for i in range(steps):
                t = i / steps
                Color(c1[0]+t*(c2[0]-c1[0]), c1[1]+t*(c2[1]-c1[1]),
                      c1[2]+t*(c2[2]-c1[2]), 1)
                y = self.y + (i / steps) * self.height
                Rectangle(pos=(self.x, y), size=(self.width, self.height/steps + 1))


# ── Ligne de séparation ───────────────────────────────────────────────────────
class TabBar(MDBoxLayout):
    def __init__(self, on_login, on_signup, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None, height=dp(50),
            spacing=0,
            **kwargs,
        )
        self.btn_login  = MDFlatButton(
            text="Se connecter", size_hint_x=1, height=dp(50),
            font_size=dp(15),
        )
        self.btn_signup = MDFlatButton(
            text="S'inscrire", size_hint_x=1, height=dp(50),
            font_size=dp(15),
        )
        self.btn_login.bind(on_release=lambda _: on_login())
        self.btn_signup.bind(on_release=lambda _: on_signup())
        self.add_widget(self.btn_login)
        self.add_widget(self.btn_signup)
        self._set_active(0)

    def _set_active(self, idx):
        self.btn_login.text_color  = _c(PINK) if idx == 0 else _c(GRAY)
        self.btn_signup.text_color = _c(PINK) if idx == 1 else _c(GRAY)


# ── Champ de saisie helper ────────────────────────────────────────────────────
def _field(hint, password=False):
    return MDTextField(
        hint_text=hint,
        password=password,
        size_hint_y=None, height=dp(58),
    )

def _spinner(values, default):
    return Spinner(
        text=default, values=values,
        size_hint=(1, None), height=dp(46),
    )


# ── Écran principal ───────────────────────────────────────────────────────────
class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_login_success = None
        self._active_tab = 0
        self._build()

    def _build(self):
        # Racine : bannière en haut, scroll en bas
        root = BoxLayout(orientation="vertical")
        root.add_widget(Banner())

        # Barre d'onglets (fixe, hors du scroll)
        self._tabbar = TabBar(
            on_login=lambda: self._switch(0),
            on_signup=lambda: self._switch(1),
        )
        root.add_widget(self._tabbar)

        # ScrollView qui ne contient QU'UN formulaire à la fois
        self._scroll = ScrollView(size_hint=(1, 1))
        self._form_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(22), dp(12), dp(22), dp(20)],
            spacing=dp(12),
        )
        self._form_container.bind(minimum_height=self._form_container.setter("height"))
        self._scroll.add_widget(self._form_container)
        root.add_widget(self._scroll)

        self.add_widget(root)

        # Construire les deux formulaires (pas encore ajoutés)
        self._build_login_form()
        self._build_signup_form()

        # Afficher le formulaire de connexion par défaut
        self._switch(0)

    # ── Changement d'onglet ───────────────────────────────────────────────────
    def _switch(self, idx):
        self._active_tab = idx
        self._tabbar._set_active(idx)
        self._form_container.clear_widgets()
        if idx == 0:
            for w in self._login_widgets:
                self._form_container.add_widget(w)
        else:
            for w in self._signup_widgets:
                self._form_container.add_widget(w)
        # Remonter en haut du scroll
        self._scroll.scroll_y = 1

    # ── Formulaire connexion ──────────────────────────────────────────────────
    def _build_login_form(self):
        self.login_email = _field("✉  Email étudiant")
        self.login_pw    = _field("🔒  Mot de passe", password=True)

        btn = MDRaisedButton(
            text="Se connecter  →",
            size_hint=(1, None), height=dp(52),
            md_bg_color=_c(PINK),
            font_size=dp(16),
        )
        btn.bind(on_release=lambda _: self._do_login())

        self._login_widgets = [self.login_email, self.login_pw, btn]

    def _do_login(self):
        email = self.login_email.text.strip().lower()
        pw    = self.login_pw.text
        if not email or not pw:
            _popup("Erreur", "Remplis tous les champs.")
            return

        from utils import firebase_client as fb
        if fb.is_configured():
            result = fb.sign_in(email, pw)
            if result:
                key  = fb.encode_email(email)
                user = fb.db_get(f"users/{key}") or {
                    "id": result.get("localId", ""), "email": email,
                    "name": email, "avatar": "🎓", "avatar_color": "#1565C0",
                    "school": "", "major": "", "bio": "",
                    "posts": [], "badges": ["🎓 Nouveau"],
                }
                user["email_verified"] = fb.is_email_verified()
                if self.on_login_success:
                    self.on_login_success(user)
            else:
                _popup("Erreur", "Email ou mot de passe incorrect.")
            return

        from utils.data import REGISTERED_USERS
        if email not in REGISTERED_USERS:
            _popup("Erreur", "Compte introuvable.\nInscris-toi d'abord.")
            return
        if REGISTERED_USERS[email]["password_hash"] != hash_pw(pw):
            _popup("Erreur", "Mot de passe incorrect.")
            return
        user = {k: v for k, v in REGISTERED_USERS[email].items()
                if k != "password_hash"}
        if self.on_login_success:
            self.on_login_success(user)

    # ── Formulaire inscription ────────────────────────────────────────────────
    def _build_signup_form(self):
        self.su_fname  = _field("👤  Prénom")
        self.su_lname  = _field("👤  Nom")
        self.su_email  = _field("✉  Email (@ac.ma, @edu.ma…)")
        self.su_pw     = _field("🔒  Mot de passe (min. 6 car.)", password=True)
        self.su_pw2    = _field("🔒  Confirmer le mot de passe", password=True)
        self.su_school = _spinner(SCHOOLS, "🏫  École / Université")
        self.su_major  = _spinner(MAJORS,  "📖  Filière")

        terms = MDLabel(
            text="En vous inscrivant, vous confirmez\nque votre email est un email étudiant.",
            halign="center", font_style="Caption",
            theme_text_color="Custom", text_color=_c(MID_BLU),
            size_hint_y=None, height=dp(44),
        )
        btn = MDRaisedButton(
            text="Créer mon compte  ✓",
            size_hint=(1, None), height=dp(52),
            md_bg_color=_c(GREEN),
            font_size=dp(16),
        )
        btn.bind(on_release=lambda _: self._do_signup())

        self._signup_widgets = [
            self.su_fname, self.su_lname, self.su_email,
            self.su_pw, self.su_pw2,
            self.su_school, self.su_major,
            terms, btn,
        ]

    def _do_signup(self):
        fname  = self.su_fname.text.strip()
        lname  = self.su_lname.text.strip()
        email  = self.su_email.text.strip().lower()
        pw     = self.su_pw.text
        pw2    = self.su_pw2.text
        school = self.su_school.text
        major  = self.su_major.text

        if not all([fname, lname, email, pw, pw2]):
            _popup("Erreur", "Remplis tous les champs obligatoires.")
            return
        if "École" in school or not school:
            _popup("Erreur", "Sélectionne ton école.")
            return
        if "Filière" in major or not major:
            _popup("Erreur", "Sélectionne ta filière.")
            return
        if pw != pw2:
            _popup("Erreur", "Les mots de passe ne correspondent pas.")
            return
        if len(pw) < 6:
            _popup("Erreur", "Mot de passe trop court (min. 6 caractères).")
            return

        user_id  = f"user_{int(time.time())}_{random.randint(1000, 9999)}"
        new_user = {
            "id":           user_id,
            "name":         f"{fname} {lname}",
            "email":        email,
            "school":       school,
            "major":        major,
            "avatar":       random.choice(AVATARS),
            "avatar_color": random.choice(COLORS),
            "bio":          f"Étudiant(e) en {major} à {school}.",
            "posts":        [],
            "badges":       ["🎓 Nouveau"],
            "created_at":   time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        from utils import firebase_client as fb
        if fb.is_configured():
            result = fb.sign_up(email, pw)
            if not result:
                _popup("Erreur", "Erreur création du compte.\nCet email est peut-être déjà utilisé.")
                return
            new_user["id"] = result.get("localId", user_id)
            fb.db_set(f"users/{fb.encode_email(email)}", new_user)
            fb.send_email_verification()
            _popup("Email envoyé 📧",
                   f"Confirme ton adresse :\n{email}\n\nPuis connecte-toi.")
            self._switch(0)
            self.login_email.text = email
            return

        new_user["password_hash"] = hash_pw(pw)
        from utils.data import REGISTERED_USERS, save_users
        if email in REGISTERED_USERS:
            _popup("Erreur", "Cet email est déjà utilisé.")
            return
        REGISTERED_USERS[email] = new_user
        save_users()

        user = {k: v for k, v in new_user.items() if k != "password_hash"}
        if self.on_login_success:
            self.on_login_success(user)
