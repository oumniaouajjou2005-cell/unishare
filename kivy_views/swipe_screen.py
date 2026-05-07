from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import (Color, RoundedRectangle, Rectangle,
                            Line, Ellipse)
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.text import LabelBase

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

PINK       = "#1565C0"
GREEN      = "#43A047"
YELLOW     = "#F9A825"
DARK       = "#212121"
GRAY       = "#757575"
LIGHT      = "#E3F2FD"
WHITE      = "#FFFFFF"
NOPE_COLOR = "#E53935"


def _hex(h):
    c = get_color_from_hex(h)
    return (c[0], c[1], c[2], 1)


# ── Swipe Card (fonctionne avec touch desktop ET mobile) ──────────────────────
class SwipeCard(Widget):
    CARD_W = dp(320)
    CARD_H = dp(480)

    def __init__(self, user_data, controller, swipe_view, **kwargs):
        super().__init__(**kwargs)
        self.user = user_data
        self.controller = controller
        self.swipe_view = swipe_view
        self.swipe_completed = False

        self._start_x = 0
        self._start_y = 0
        self._origin_x = 0
        self._origin_y = 0

        self.size_hint = (None, None)
        self.size = (self.CARD_W, self.CARD_H)

        self._build_canvas()
        self._overlay = self._make_overlay()
        self.add_widget(self._overlay)

    def _build_canvas(self):
        color = self.user.get("avatar_color", "#3498db")
        self.bind(size=self._redraw, pos=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        color = self.user.get("avatar_color", "#3498db")
        c = get_color_from_hex(color)
        W, H = self.CARD_W, self.CARD_H
        photo_h = int(H * 0.72)

        with self.canvas.before:
            # Card shadow
            Color(0, 0, 0, 0.12)
            RoundedRectangle(
                pos=(self.x + dp(4), self.y - dp(4)),
                size=(W, H), radius=[dp(22)]
            )
            # Photo background (gradient with avatar color)
            c_light = (min(c[0] * 1.3, 1), min(c[1] * 1.3, 1), min(c[2] * 1.3, 1), 1)
            Color(*c_light)
            RoundedRectangle(pos=(self.x, self.y + H - photo_h),
                              size=(W, photo_h), radius=[dp(22), dp(22), 0, 0])
            # Dark overlay at bottom of photo
            Color(0, 0, 0, 0.5)
            Rectangle(pos=(self.x, self.y + H - photo_h),
                       size=(W, dp(80)))
            # White info panel
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=(self.x, self.y),
                              size=(W, H - photo_h + dp(10)),
                              radius=[0, 0, dp(22), dp(22)])

        # Name label on photo
        self.canvas.after.clear()
        with self.canvas.after:
            Color(1, 1, 1, 1)

    def _make_overlay(self):
        overlay = FloatLayout(size_hint=(1, 1))

        # Avatar emoji (big, centered in photo area)
        photo_h_ratio = 0.72
        avatar_lbl = Label(
            text=self.user.get("avatar", "👤"),
            font_size=dp(80),
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            pos_hint={"center_x": 0.5, "top": photo_h_ratio + 0.05},
        )
        overlay.add_widget(avatar_lbl)

        # Name + age label
        name_lbl = Label(
            text=f"{self.user.get('name', '')}",
            font_size=dp(20),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(32),
            pos_hint={"x": 0, "top": photo_h_ratio - 0.01},
            halign="left",
            padding_x=dp(16),
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))
        overlay.add_widget(name_lbl)

        # School
        school_lbl = Label(
            text=f"🏫 {self.user.get('school', '')}",
            font_size=dp(12),
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, None),
            height=dp(24),
            pos_hint={"x": 0, "top": photo_h_ratio - 0.07},
            halign="left",
            padding_x=dp(16),
        )
        school_lbl.bind(size=school_lbl.setter("text_size"))
        overlay.add_widget(school_lbl)

        # Major pill (info panel)
        major_lbl = Label(
            text=f"📖 {self.user.get('major', '')}",
            font_size=dp(13),
            bold=True,
            color=_hex(PINK)[:3] + (1,),
            size_hint=(None, None),
            size=(dp(180), dp(30)),
            pos_hint={"x": 0.04, "y": 0.24},
        )
        overlay.add_widget(major_lbl)

        # Bio
        bio_lbl = Label(
            text=(self.user.get("bio", "")[:70] + "…") if len(self.user.get("bio", "")) > 70
                 else self.user.get("bio", ""),
            font_size=dp(12),
            color=get_color_from_hex(GRAY),
            size_hint=(1, None),
            height=dp(50),
            pos_hint={"x": 0, "y": 0.09},
            halign="left",
            valign="top",
            padding_x=dp(16),
        )
        bio_lbl.bind(size=bio_lbl.setter("text_size"))
        overlay.add_widget(bio_lbl)

        # LIKE / NOPE overlay labels (hidden by default)
        self._like_lbl = Label(
            text="LIKE ✓",
            font_size=dp(28),
            bold=True,
            color=(0.26, 0.63, 0.28, 0),
            size_hint=(None, None),
            size=(dp(130), dp(56)),
            pos_hint={"x": 0.04, "top": 0.93},
        )
        self._nope_lbl = Label(
            text="NOPE ✗",
            font_size=dp(28),
            bold=True,
            color=(0.9, 0.12, 0.18, 0),
            size_hint=(None, None),
            size=(dp(130), dp(56)),
            pos_hint={"right": 0.96, "top": 0.93},
        )
        overlay.add_widget(self._like_lbl)
        overlay.add_widget(self._nope_lbl)

        return overlay

    # ── Touch events (fonctionne desktop ET mobile) ───────────────────────────

    def on_touch_down(self, touch):
        if self.swipe_completed:
            return False
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._start_x  = touch.x
            self._start_y  = touch.y
            self._origin_x = self.center_x
            self._origin_y = self.center_y
            return True
        return False

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return False
        dx = touch.x - self._start_x
        dy = touch.y - self._start_y
        self.center_x = self._origin_x + dx
        self.center_y = self._origin_y + dy

        if dx > dp(30):
            self._like_lbl.color = (0.26, 0.63, 0.28, min(abs(dx) / dp(100), 1))
            self._nope_lbl.color = (*get_color_from_hex(NOPE_COLOR)[:3], 0)
        elif dx < -dp(30):
            self._nope_lbl.color = (*get_color_from_hex(NOPE_COLOR)[:3],
                                     min(abs(dx) / dp(100), 1))
            self._like_lbl.color = (0.26, 0.63, 0.28, 0)
        else:
            self._like_lbl.color = (0.26, 0.63, 0.28, 0)
            self._nope_lbl.color = (*get_color_from_hex(NOPE_COLOR)[:3], 0)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return False
        touch.ungrab(self)

        dx = self.center_x - self._origin_x
        dy = self.center_y - self._origin_y

        if abs(dx) > dp(80):
            if dx > 0:
                self._swipe_right()
            else:
                self._swipe_left()
        elif dy < -dp(80):
            self._swipe_down()
        else:
            self._return_to_origin()
        return True

    def _return_to_origin(self):
        self._like_lbl.color = (0.26, 0.63, 0.28, 0)
        self._nope_lbl.color = (*get_color_from_hex(NOPE_COLOR)[:3], 0)
        anim = Animation(center_x=self._origin_x, center_y=self._origin_y,
                         d=0.2, t="out_cubic")
        anim.start(self)

    def swipe_left(self):
        if self.swipe_completed:
            return
        self.swipe_completed = True
        anim = Animation(center_x=-self.CARD_W, d=0.3, t="out_cubic")
        anim.bind(on_complete=lambda *_: self._close_card())
        anim.start(self)

    def swipe_right(self):
        if self.swipe_completed:
            return
        self.swipe_completed = True
        from kivy.core.window import Window
        anim = Animation(center_x=Window.width + self.CARD_W, d=0.3, t="out_cubic")
        anim.bind(on_complete=lambda *_: self._after_right())
        anim.start(self)

    def swipe_down(self):
        if self.swipe_completed:
            return
        self.swipe_completed = True
        anim = Animation(center_y=-self.CARD_H, d=0.3, t="out_cubic")
        anim.bind(on_complete=lambda *_: self._close_card())
        anim.start(self)
        self.swipe_view.save_for_later(self.user)

    _swipe_left  = swipe_left
    _swipe_right = swipe_right
    _swipe_down  = swipe_down

    def _close_card(self):
        if self.parent:
            self.parent.remove_widget(self)
        self.swipe_view.load_next_card()

    def _after_right(self):
        if self.parent:
            self.parent.remove_widget(self)
        self.swipe_view.after_swipe_right(self.user)


# ── SwipeScreen ───────────────────────────────────────────────────────────────
class SwipeScreen(MDScreen):
    def __init__(self, controller, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.controller  = controller
        self.main_screen = main_screen
        self.current_users = []
        self.current_index = 0
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # ── Top bar ───────────────────────────────────────────────────────────
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(52),
            padding=[dp(16), dp(8)],
            spacing=dp(8),
            md_bg_color=_hex(WHITE),
        )
        top_bar.add_widget(MDLabel(
            text="🎓 UniShare",
            font_style="H6",
            theme_text_color="Custom",
            text_color=_hex(PINK),
        ))
        top_bar.add_widget(Widget())
        later_btn = MDRaisedButton(
            text="⏰ Plus tard",
            size_hint_x=None,
            md_bg_color=_hex(YELLOW),
        )
        later_btn.bind(on_release=lambda _: self._show_saved())
        top_bar.add_widget(later_btn)
        root.add_widget(top_bar)

        # ── Indicators ────────────────────────────────────────────────────────
        ind_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(32),
            padding=[dp(20), dp(4)],
        )
        for txt, color in [("✗ Passer", NOPE_COLOR), ("⏰ Plus tard", YELLOW), ("🤝 Match", GREEN)]:
            lbl = MDLabel(
                text=txt, halign="center",
                theme_text_color="Custom",
                text_color=_hex(color),
            )
            ind_bar.add_widget(lbl)
        root.add_widget(ind_bar)

        # ── Card container ────────────────────────────────────────────────────
        self.card_container = FloatLayout(size_hint=(1, 1))
        root.add_widget(self.card_container)

        # ── Action buttons ────────────────────────────────────────────────────
        btn_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(90),
            padding=[dp(40), dp(10)],
            spacing=dp(20),
        )
        btn_bar.add_widget(Widget())

        self.btn_nope = self._make_circle_btn("✗", "#FFEBEE", NOPE_COLOR, dp(60))
        self.btn_nope.bind(on_release=lambda _: self._on_nope())
        btn_bar.add_widget(self.btn_nope)

        self.btn_later = self._make_circle_btn("⏰", "#FFF9C4", YELLOW, dp(50))
        self.btn_later.bind(on_release=lambda _: self._on_later())
        btn_bar.add_widget(self.btn_later)

        self.btn_like = self._make_circle_btn("🤝", "#E8F5E9", GREEN, dp(60))
        self.btn_like.bind(on_release=lambda _: self._on_like())
        btn_bar.add_widget(self.btn_like)

        btn_bar.add_widget(Widget())
        root.add_widget(btn_bar)

        # ── Info label ────────────────────────────────────────────────────────
        self.info_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Custom",
            text_color=_hex(GRAY),
            size_hint_y=None, height=dp(24),
            font_style="Caption",
        )
        root.add_widget(self.info_label)

        self.add_widget(root)
        self.refresh_users()

    @staticmethod
    def _make_circle_btn(icon, bg_hex, border_hex, size):
        btn = MDRaisedButton(
            text=icon,
            size_hint=(None, None),
            size=(size, size),
            md_bg_color=_hex(bg_hex),
            font_size=size * 0.4,
        )
        return btn

    # ── Card management ───────────────────────────────────────────────────────

    def refresh_users(self):
        self.current_users = self.controller.get_users_to_swipe()
        self.current_index = 0
        self.load_next_card()

    def load_next_card(self):
        self.card_container.clear_widgets()

        if not self.current_users:
            self._show_empty()
            return

        if self.current_index >= len(self.current_users):
            if self.controller.endless_mode:
                self.current_index = 0
            else:
                self._show_empty()
                return

        user = self.current_users[self.current_index]
        card = SwipeCard(user, self.controller, self)

        # Center the card
        from kivy.core.window import Window
        card.center_x = Window.width / 2
        card.center_y = Window.height / 2
        self.card_container.add_widget(card)

        self.current_index += 1
        remaining = len(self.current_users) - self.current_index % len(self.current_users)
        self.info_label.text = f"👥 {remaining} profil(s) à découvrir • Glisse ou clique !"

    def _show_empty(self):
        self.card_container.clear_widgets()
        lbl = MDLabel(
            text="🎉 Plus de profils !\nReviens bientôt…",
            halign="center",
            theme_text_color="Custom",
            text_color=_hex(GRAY),
            font_style="H6",
        )
        self.card_container.add_widget(lbl)
        self.info_label.text = ""

    def _on_nope(self):
        for w in self.card_container.children[:]:
            if isinstance(w, SwipeCard):
                w.swipe_left()
                return

    def _on_like(self):
        for w in self.card_container.children[:]:
            if isinstance(w, SwipeCard):
                w.swipe_right()
                return

    def _on_later(self):
        for w in self.card_container.children[:]:
            if isinstance(w, SwipeCard):
                w.swipe_down()
                return

    def after_swipe_right(self, user):
        import utils.data as data_module
        current = data_module.CURRENT_USER or {}
        try:
            from utils import api_client
            api_client.send_follow_request(current, user.get("id", ""))
        except Exception:
            pass
        self._show_toast(f"📨 Demande envoyée à {user.get('name', '')}")
        self.load_next_card()

    def save_for_later(self, user):
        if not self.controller.is_saved_for_later(user["id"]):
            self.controller.save_for_later(user)
            self._show_toast(f"✅ {user['name']} ajouté à Plus tard")

    def _show_toast(self, message):
        lbl = MDLabel(
            text=message,
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(280), dp(44)),
            pos_hint={"center_x": 0.5, "y": 0.12},
        )
        from kivy.graphics import Color, RoundedRectangle
        with lbl.canvas.before:
            Color(0.13, 0.13, 0.13, 0.88)
            lbl._bg = RoundedRectangle(pos=lbl.pos, size=lbl.size, radius=[dp(22)])
        lbl.bind(pos=lambda w, v: setattr(lbl._bg, "pos", v),
                 size=lambda w, v: setattr(lbl._bg, "size", v))
        self.card_container.add_widget(lbl)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.card_container.remove_widget(lbl), 2.5)

    def _show_saved(self):
        later_users = self.controller.get_later_users()
        if not later_users:
            self._show_toast("📭 Aucun profil sauvegardé")
            return

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        scroll = ScrollView()
        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        inner.bind(minimum_height=inner.setter("height"))

        for user in later_users:
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None, height=dp(60),
                spacing=dp(10), padding=[dp(8), dp(4)],
                md_bg_color=_hex("#F5F5F5"),
            )
            row.add_widget(MDLabel(
                text=f"{user.get('avatar','👤')}  {user.get('name','')}",
                theme_text_color="Custom",
                text_color=_hex(DARK),
            ))
            btn = MDRaisedButton(
                text="Voir",
                size_hint_x=None,
                md_bg_color=_hex(PINK),
            )
            _u = user

            def _open(_, u=_u, popup_ref=[None]):
                if popup_ref[0]:
                    popup_ref[0].dismiss()
                self._show_profile_detail(u)

            btn.bind(on_release=_open)
            row.add_widget(btn)
            inner.add_widget(row)

        scroll.add_widget(inner)
        content.add_widget(scroll)

        close_btn = MDRaisedButton(text="Fermer", size_hint=(1, None), height=dp(44))
        content.add_widget(close_btn)

        popup = Popup(title="⏰ Profils sauvegardés",
                      content=content,
                      size_hint=(0.9, 0.7))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _show_profile_detail(self, user):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(MDLabel(
            text=f"{user.get('avatar','👤')}  {user.get('name','')}",
            font_style="H5", halign="center",
        ))
        content.add_widget(MDLabel(text=f"🏫 {user.get('school','')}", halign="center"))
        content.add_widget(MDLabel(text=f"📖 {user.get('major','')}", halign="center"))
        if user.get("bio"):
            content.add_widget(MDLabel(text=user["bio"], halign="center"))

        chat_btn = MDRaisedButton(
            text=f"💬 Chatter avec {user.get('name','')}",
            size_hint=(1, None), height=dp(48),
            md_bg_color=_hex(PINK),
        )
        close_btn = MDFlatButton(text="Fermer", size_hint=(1, None), height=dp(44))
        content.add_widget(chat_btn)
        content.add_widget(close_btn)

        popup = Popup(title="Profil",
                      content=content,
                      size_hint=(0.88, 0.65))

        def _chat(_):
            popup.dismiss()
            self.main_screen.go_to_chat_with(user)

        chat_btn.bind(on_release=_chat)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
