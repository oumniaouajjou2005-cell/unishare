import random
import time as _time

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard

PINK    = "#1565C0"
BLUE_BG = "#1565C0"
GRAY_BG = "#EEEEEE"
DARK    = "#212121"
GRAY    = "#757575"
WHITE   = "#FFFFFF"
LIGHT   = "#E3F2FD"

AUTO_REPLIES = [
    "Salut ! Comment ça va ? 😊",
    "Super idée, on peut réviser ensemble !",
    "Tu as des fiches à partager ?",
    "Intéressant ! Dis m'en plus.",
    "Je suis dispo ce week-end 📚",
    "Merci pour le partage 👍",
    "On peut se retrouver à la bibliothèque ?",
    "Tu étudies quelle filière ?",
    "J'adore cette initiative ! 🎓",
    "On reste en contact 😄",
]


def _hex(h):
    c = get_color_from_hex(h)
    return (c[0], c[1], c[2], 1)


# ── Message bubble ────────────────────────────────────────────────────────────
class MessageBubble(MDBoxLayout):
    def __init__(self, msg, is_mine, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            padding=[dp(8), dp(3)],
            spacing=dp(8),
            **kwargs,
        )
        text  = msg.get("text", "")
        t_str = msg.get("time", "")

        if is_mine:
            self.add_widget(Widget())
            bubble = MDBoxLayout(
                orientation="vertical",
                size_hint=(None, None),
                padding=[dp(12), dp(8)],
                spacing=dp(2),
                md_bg_color=_hex(BLUE_BG),
            )
            bubble.add_widget(MDLabel(
                text=text, size_hint_y=None,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                halign="right",
            ))
            if t_str:
                bubble.add_widget(MDLabel(
                    text=t_str, font_style="Caption",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.9, 0.9, 0.8),
                    halign="right", size_hint_y=None, height=dp(16),
                ))
            bubble.bind(minimum_height=bubble.setter("height"))
            # Approximate width
            bubble.width = min(dp(240), dp(16) + len(text) * dp(8))
            self.add_widget(bubble)
        else:
            avatar_lbl = MDLabel(
                text=msg.get("avatar", "👤"),
                font_size=dp(26),
                size_hint=(None, None), size=(dp(36), dp(36)),
                halign="center",
            )
            self.add_widget(avatar_lbl)
            bubble = MDBoxLayout(
                orientation="vertical",
                size_hint=(None, None),
                padding=[dp(12), dp(8)],
                spacing=dp(2),
                md_bg_color=_hex(GRAY_BG),
            )
            bubble.add_widget(MDLabel(
                text=text, size_hint_y=None,
                theme_text_color="Custom",
                text_color=_hex(DARK),
                halign="left",
            ))
            if t_str:
                bubble.add_widget(MDLabel(
                    text=t_str, font_style="Caption",
                    theme_text_color="Custom",
                    text_color=_hex(GRAY),
                    halign="left", size_hint_y=None, height=dp(16),
                ))
            bubble.bind(minimum_height=bubble.setter("height"))
            bubble.width = min(dp(240), dp(16) + len(text) * dp(8))
            self.add_widget(bubble)
            self.add_widget(Widget())

        self.bind(minimum_height=self.setter("height"))


# ── Individual Chat View ──────────────────────────────────────────────────────
class ChatView(MDBoxLayout):
    def __init__(self, controller, main_screen, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.controller  = controller
        self.main_screen = main_screen
        self.partner     = None
        self._messages   = []
        self._build_ui()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        self.hdr = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(54),
            padding=[dp(8), dp(6)],
            spacing=dp(8),
            md_bg_color=_hex(PINK),
        )
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
        )
        back_btn.bind(on_release=lambda _: self.main_screen.go_to_chats())
        self.hdr.add_widget(back_btn)

        self.partner_lbl = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6",
        )
        self.hdr.add_widget(self.partner_lbl)
        self.add_widget(self.hdr)

        # ── Messages scroll ───────────────────────────────────────────────────
        self.scroll = ScrollView(size_hint=(1, 1))
        self.messages_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
            padding=[0, dp(8), 0, dp(8)],
        )
        self.messages_layout.bind(minimum_height=self.messages_layout.setter("height"))
        self.scroll.add_widget(self.messages_layout)
        self.add_widget(self.scroll)

        # ── Input bar ─────────────────────────────────────────────────────────
        input_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(60),
            padding=[dp(8), dp(6)],
            spacing=dp(8),
            md_bg_color=(1, 1, 1, 1),
        )
        self.text_input = MDTextField(
            hint_text="Écrire un message…",
            size_hint_x=1,
        )
        self.text_input.bind(on_text_validate=lambda _: self._send_message())

        send_btn = MDRaisedButton(
            text="▶",
            size_hint=(None, None),
            size=(dp(48), dp(44)),
            md_bg_color=_hex(PINK),
        )
        send_btn.bind(on_release=lambda _: self._send_message())
        input_bar.add_widget(self.text_input)
        input_bar.add_widget(send_btn)
        self.add_widget(input_bar)

    def set_partner(self, user_dict):
        self.partner = user_dict
        self.partner_lbl.text = (
            f"{user_dict.get('avatar','👤')}  {user_dict.get('name','')}"
        )
        self._load_messages()

    def _load_messages(self):
        self.messages_layout.clear_widgets()
        if not self.partner:
            return
        conv_id = self.partner.get("id", "")
        self._messages = self.controller.get_messages(conv_id)
        for msg in self._messages:
            bubble = MessageBubble(msg, is_mine=msg.get("is_mine", True))
            self.messages_layout.add_widget(bubble)
        self._scroll_bottom()

    def _send_message(self):
        text = self.text_input.text.strip()
        if not text or not self.partner:
            return
        self.text_input.text = ""

        import utils.data as data_module
        user = data_module.CURRENT_USER or {}
        msg = {
            "text": text,
            "is_mine": True,
            "avatar": user.get("avatar", "👤"),
            "time": _time.strftime("%H:%M"),
        }
        self._messages.append(msg)
        self.controller.save_message(self.partner.get("id", ""), msg)
        bubble = MessageBubble(msg, is_mine=True)
        self.messages_layout.add_widget(bubble)
        self._scroll_bottom()

        # Auto reply
        Clock.schedule_once(lambda dt: self._auto_reply(), random.uniform(0.8, 2.0))

    def _auto_reply(self):
        if not self.partner:
            return
        msg = {
            "text": random.choice(AUTO_REPLIES),
            "is_mine": False,
            "avatar": self.partner.get("avatar", "👤"),
            "time": _time.strftime("%H:%M"),
        }
        self._messages.append(msg)
        self.controller.save_message(self.partner.get("id", ""), msg)
        bubble = MessageBubble(msg, is_mine=False)
        self.messages_layout.add_widget(bubble)
        self._scroll_bottom()

    def _scroll_bottom(self):
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.1)


# ── Chats list (conversation list) ───────────────────────────────────────────
class ChatsScreen(MDScreen):
    def __init__(self, controller, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.controller  = controller
        self.main_screen = main_screen
        self._conversations = []
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # ── Header ────────────────────────────────────────────────────────────
        hdr = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(54),
            padding=[dp(14), dp(10)],
            md_bg_color=(1, 1, 1, 1),
        )
        hdr.add_widget(MDLabel(
            text="💬 Mes Conversations",
            font_style="H6",
            theme_text_color="Custom",
            text_color=_hex(PINK),
        ))
        root.add_widget(hdr)

        # ── Conversations scroll ──────────────────────────────────────────────
        self.scroll = ScrollView(size_hint=(1, 1))
        self.conv_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(1),
        )
        self.conv_layout.bind(minimum_height=self.conv_layout.setter("height"))
        self.scroll.add_widget(self.conv_layout)

        # ── Chat view (embedded, shown when a conversation is open) ───────────
        self.chat_view = ChatView(
            controller=self.controller,
            main_screen=self.main_screen,
            size_hint=(1, 1),
        )
        self.chat_view.opacity = 0
        self.chat_view.disabled = True

        # Use a top-level FloatLayout-like container
        self._chats_container = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self._chats_container.add_widget(self.scroll)
        root.add_widget(self._chats_container)

        self.add_widget(root)
        self._root = root

    def add_conversation(self, user_dict):
        uid = user_dict.get("id", "")
        for existing in self._conversations:
            if existing.get("id") == uid:
                return
        self._conversations.append(user_dict)
        self._refresh_list()

    def _refresh_list(self):
        self.conv_layout.clear_widgets()
        if not self._conversations:
            self.conv_layout.add_widget(MDLabel(
                text="💬 Aucune conversation\n\nFais un match dans Swipe pour commencer !",
                halign="center",
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                size_hint_y=None, height=dp(160),
            ))
            return

        for user in self._conversations:
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None, height=dp(68),
                padding=[dp(14), dp(10)],
                spacing=dp(12),
                md_bg_color=(1, 1, 1, 1),
            )
            row.add_widget(MDLabel(
                text=user.get("avatar", "👤"),
                font_size=dp(34),
                size_hint=(None, None), size=(dp(48), dp(48)),
                halign="center",
            ))
            info = BoxLayout(orientation="vertical", spacing=dp(2))
            info.add_widget(MDLabel(
                text=user.get("name", ""),
                theme_text_color="Custom",
                text_color=_hex(DARK),
                font_style="Subtitle1",
                size_hint_y=None, height=dp(24),
            ))
            info.add_widget(MDLabel(
                text=user.get("school", ""),
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                font_style="Caption",
                size_hint_y=None, height=dp(18),
            ))
            row.add_widget(info)
            row.add_widget(Widget())

            _u = user
            row.bind(on_touch_down=lambda widget, touch, u=_u:
                     self._row_touch(widget, touch, u))
            self.conv_layout.add_widget(row)

    def _row_touch(self, widget, touch, user):
        if widget.collide_point(*touch.pos):
            self.open_chat(user)
            return True
        return False

    def open_chat(self, user_dict):
        self.chat_view.set_partner(user_dict)
        self._chats_container.clear_widgets()
        self._chats_container.add_widget(self.chat_view)
        self.chat_view.opacity = 1
        self.chat_view.disabled = False

    def show_list(self):
        self.chat_view.opacity = 0
        self.chat_view.disabled = True
        self._chats_container.clear_widgets()
        self._chats_container.add_widget(self.scroll)

    def go_to_chats(self):
        self.show_list()
