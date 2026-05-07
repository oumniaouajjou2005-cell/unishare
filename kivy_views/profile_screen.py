from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField

import utils.data as data_module

PINK  = "#1565C0"
DARK  = "#212121"
GRAY  = "#757575"
LIGHT = "#E3F2FD"
WHITE = "#FFFFFF"
GREEN = "#43A047"
BLUE  = "#1565C0"
RED   = "#E53935"

LANGS = ["Français", "English", "العربية"]

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


def _hex(h):
    c = get_color_from_hex(h)
    return (c[0], c[1], c[2], 1)


# ── Profile Screen ────────────────────────────────────────────────────────────
class ProfileScreen(MDScreen):
    def __init__(self, controller, main_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.controller  = controller
        self.main_screen = main_screen
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")
        self.scroll = ScrollView(size_hint=(1, 1))
        self.content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        root.add_widget(self.scroll)
        self.add_widget(root)
        self._render()

    def _render(self):
        self.content.clear_widgets()
        user = data_module.CURRENT_USER or {}

        # ── Profile header card ───────────────────────────────────────────────
        hdr_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(10),
            elevation=2,
        )
        hdr_card.bind(minimum_height=hdr_card.setter("height"))

        # Avatar + edit button row
        avatar_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(80),
            spacing=dp(16),
        )
        avatar_lbl = MDLabel(
            text=user.get("avatar", "👤"),
            font_size=dp(56),
            size_hint=(None, None), size=(dp(72), dp(72)),
            halign="center",
        )
        avatar_row.add_widget(avatar_lbl)

        info_col = BoxLayout(orientation="vertical", spacing=dp(4))
        info_col.add_widget(MDLabel(
            text=user.get("name", ""),
            font_style="H5", bold=True,
            theme_text_color="Custom",
            text_color=_hex(DARK),
            size_hint_y=None, height=dp(34),
        ))
        info_col.add_widget(MDLabel(
            text=user.get("email", ""),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=_hex(GRAY),
            size_hint_y=None, height=dp(20),
        ))
        info_col.add_widget(MDLabel(
            text=f"🏫 {user.get('school','')}  •  📖 {user.get('major','')}",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=_hex(PINK),
            size_hint_y=None, height=dp(20),
        ))
        avatar_row.add_widget(info_col)
        hdr_card.add_widget(avatar_row)

        # Bio
        if user.get("bio"):
            hdr_card.add_widget(MDLabel(
                text=user.get("bio", ""),
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                font_style="Body2",
                size_hint_y=None,
            ))

        # Stats row (followers, following, posts)
        stats = self.controller.get_stats() if hasattr(self.controller, "get_stats") else {}
        stats_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(60),
        )
        for label, val in [
            ("Publications", len(user.get("posts", []))),
            ("Abonnés",      stats.get("followers", 0)),
            ("Abonnements",  stats.get("following", 0)),
        ]:
            col = BoxLayout(orientation="vertical")
            col.add_widget(MDLabel(
                text=str(val),
                halign="center", bold=True,
                theme_text_color="Custom",
                text_color=_hex(DARK),
                font_style="H6",
                size_hint_y=None, height=dp(30),
            ))
            col.add_widget(MDLabel(
                text=label,
                halign="center",
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                font_style="Caption",
                size_hint_y=None, height=dp(20),
            ))
            stats_row.add_widget(col)
        hdr_card.add_widget(stats_row)

        # Edit profile button
        edit_btn = MDRaisedButton(
            text="✏️ Modifier le profil",
            size_hint=(1, None), height=dp(44),
            md_bg_color=_hex(PINK),
        )
        edit_btn.bind(on_release=lambda _: self._show_edit_dialog())
        hdr_card.add_widget(edit_btn)

        self.content.add_widget(hdr_card)

        # ── Badges ────────────────────────────────────────────────────────────
        badges = user.get("badges", [])
        if badges:
            badge_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                padding=dp(14),
                spacing=dp(8),
                elevation=1,
            )
            badge_card.bind(minimum_height=badge_card.setter("height"))
            badge_card.add_widget(MDLabel(
                text="🏆 Mes Badges",
                bold=True, font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=_hex(DARK),
                size_hint_y=None, height=dp(30),
            ))
            badges_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None, height=dp(40),
                spacing=dp(8),
            )
            for badge in badges:
                badges_row.add_widget(MDLabel(
                    text=badge, font_size=dp(22),
                    size_hint=(None, None), size=(dp(80), dp(36)),
                    halign="center",
                ))
            badge_card.add_widget(badges_row)
            self.content.add_widget(badge_card)

        # ── My posts ──────────────────────────────────────────────────────────
        posts = self.controller.get_user_posts() if hasattr(self.controller, "get_user_posts") else []
        posts_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(14),
            spacing=dp(8),
            elevation=1,
        )
        posts_card.bind(minimum_height=posts_card.setter("height"))
        posts_card.add_widget(MDLabel(
            text="📱 Mes Publications",
            bold=True, font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=_hex(DARK),
            size_hint_y=None, height=dp(30),
        ))
        if not posts:
            posts_card.add_widget(MDLabel(
                text="Aucune publication pour le moment",
                halign="center",
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                font_style="Caption",
                size_hint_y=None, height=dp(40),
            ))
        else:
            for post in posts[:5]:
                posts_card.add_widget(MDLabel(
                    text=f"• {post.get('content','')[:60]}…",
                    theme_text_color="Custom",
                    text_color=_hex(DARK),
                    font_style="Body2",
                    size_hint_y=None, height=dp(30),
                ))
        self.content.add_widget(posts_card)

        # ── Settings / Actions ────────────────────────────────────────────────
        settings_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(14),
            spacing=dp(8),
            elevation=1,
        )
        settings_card.bind(minimum_height=settings_card.setter("height"))
        settings_card.add_widget(MDLabel(
            text="⚙️ Paramètres",
            bold=True, font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=_hex(DARK),
            size_hint_y=None, height=dp(30),
        ))

        # Language selector
        lang_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(48),
            spacing=dp(10),
        )
        lang_row.add_widget(MDLabel(
            text="🌐 Langue",
            theme_text_color="Custom",
            text_color=_hex(DARK),
            size_hint_x=0.4,
        ))
        current_lang = data_module.APP_SETTINGS.get("language", "Français")
        lang_spin = Spinner(
            text=current_lang,
            values=LANGS,
            size_hint=(0.6, None), height=dp(40),
        )
        lang_spin.bind(text=lambda _, v: self._set_language(v))
        lang_row.add_widget(lang_spin)
        settings_card.add_widget(lang_row)

        # Logout button
        logout_btn = MDRaisedButton(
            text="🚪 Se déconnecter",
            size_hint=(1, None), height=dp(44),
            md_bg_color=_hex(RED),
        )
        logout_btn.bind(on_release=lambda _: self._logout())
        settings_card.add_widget(logout_btn)
        self.content.add_widget(settings_card)

    def _set_language(self, lang):
        data_module.APP_SETTINGS["language"] = lang

    def _show_edit_dialog(self):
        user = data_module.CURRENT_USER or {}
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))

        name_inp = MDTextField(
            hint_text="Nom complet",
            text=user.get("name", ""),
            size_hint_y=None, height=dp(54),
        )
        bio_inp = MDTextField(
            hint_text="Bio…",
            text=user.get("bio", ""),
            multiline=True,
            size_hint_y=None, height=dp(80),
        )
        school_spin = Spinner(
            text=user.get("school", SCHOOLS[0]),
            values=SCHOOLS,
            size_hint_y=None, height=dp(46),
        )
        major_spin = Spinner(
            text=user.get("major", MAJORS[0]),
            values=MAJORS,
            size_hint_y=None, height=dp(46),
        )
        for w in [name_inp, bio_inp, school_spin, major_spin]:
            content.add_widget(w)

        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = MDFlatButton(text="Annuler", size_hint_x=1)
        save_btn = MDRaisedButton(
            text="💾 Sauvegarder",
            size_hint_x=1,
            md_bg_color=_hex(GREEN),
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Modifier le profil",
                      content=content,
                      size_hint=(0.92, None), height=dp(440))

        def _save(_):
            user["name"]   = name_inp.text.strip() or user.get("name", "")
            user["bio"]    = bio_inp.text.strip()
            user["school"] = school_spin.text
            user["major"]  = major_spin.text
            data_module.CURRENT_USER = user

            try:
                from utils import firebase_client as fb
                if fb.is_configured():
                    key = fb.encode_email(user.get("email", ""))
                    fb.db_set(f"users/{key}", user)
            except Exception:
                pass

            try:
                from utils.data import save_users, REGISTERED_USERS
                email = user.get("email", "")
                if email in REGISTERED_USERS:
                    REGISTERED_USERS[email].update(user)
                    save_users()
            except Exception:
                pass

            popup.dismiss()
            self._render()

        save_btn.bind(on_release=_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _logout(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(MDLabel(
            text="Voulez-vous vraiment vous déconnecter ?",
            halign="center", size_hint_y=None, height=dp(48),
        ))
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = MDFlatButton(text="Annuler", size_hint_x=1)
        logout_btn = MDRaisedButton(
            text="Se déconnecter",
            size_hint_x=1,
            md_bg_color=_hex(RED),
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(logout_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Déconnexion",
                      content=content,
                      size_hint=(0.82, None), height=dp(200))

        def _do_logout(_):
            popup.dismiss()
            try:
                from utils import firebase_client as fb
                fb.clear_session()
            except Exception:
                pass
            data_module.CURRENT_USER = None
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            app.sm.current = "login"

        logout_btn.bind(on_release=_do_logout)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def refresh(self):
        self._render()
