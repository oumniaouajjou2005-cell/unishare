import time as _time

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup

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

REACTIONS = ["❤️", "😂", "😮", "😢", "👍", "🔥"]


def _hex(h):
    c = get_color_from_hex(h)
    return (c[0], c[1], c[2], 1)


# ── Post card ─────────────────────────────────────────────────────────────────
class PostCard(MDCard):
    def __init__(self, post, controller, feed_screen, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=0,
            spacing=0,
            ripple_behavior=False,
            elevation=1,
            **kwargs,
        )
        self.post = post
        self.controller = controller
        self.feed_screen = feed_screen
        self._build()
        self.bind(minimum_height=self.setter("height"))

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(60),
            padding=[dp(12), dp(8)],
            spacing=dp(10),
        )
        avatar_lbl = MDLabel(
            text=self.post.get("user_avatar", "👤"),
            font_size=dp(30),
            size_hint=(None, None), size=(dp(46), dp(46)),
            halign="center",
        )
        hdr.add_widget(avatar_lbl)

        info = BoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(MDLabel(
            text=self.post.get("user", ""),
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=_hex(DARK),
            size_hint_y=None, height=dp(24),
        ))
        info.add_widget(MDLabel(
            text=self.post.get("date", ""),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=_hex(GRAY),
            size_hint_y=None, height=dp(18),
        ))
        hdr.add_widget(info)
        hdr.add_widget(Widget())
        self.add_widget(hdr)

        # ── Content ───────────────────────────────────────────────────────────
        content_txt = self.post.get("content", "")
        if content_txt:
            c_lbl = MDLabel(
                text=content_txt,
                theme_text_color="Custom",
                text_color=_hex(DARK),
                size_hint_y=None,
                halign="left",
                padding=[dp(14), dp(6)],
            )
            c_lbl.bind(texture_size=lambda w, v: setattr(w, "height", v[1] + dp(12)))
            self.add_widget(c_lbl)

        # ── Stats row ─────────────────────────────────────────────────────────
        likes = self.post.get("likes", 0)
        total_r = sum(self.post.get("reactions", {}).values())
        comments_count = len(self.post.get("comments", []))
        stats_parts = []
        if likes + total_r:
            stats_parts.append(f"❤️ {likes + total_r}")
        if comments_count:
            stats_parts.append(f"💬 {comments_count}")
        stats_text = "  ".join(stats_parts)

        stats_bar = MDBoxLayout(
            size_hint_y=None, height=dp(28),
            padding=[dp(14), dp(2)],
            md_bg_color=(1, 1, 1, 1),
        )
        stats_bar.add_widget(MDLabel(
            text=stats_text,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=_hex(GRAY),
        ))
        self.add_widget(stats_bar)

        # ── Reactions ─────────────────────────────────────────────────────────
        react_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(38),
            padding=[dp(6), dp(4)],
            spacing=dp(4),
        )
        self._react_btns = {}
        for emoji in REACTIONS:
            count = self.post.get("reactions", {}).get(emoji, 0)
            lbl = f"{emoji} {count}" if count else emoji
            btn = MDFlatButton(
                text=lbl,
                size_hint=(None, None),
                height=dp(30),
            )
            btn.bind(on_release=lambda _, e=emoji: self._react(e))
            react_bar.add_widget(btn)
            self._react_btns[emoji] = btn
        self.add_widget(react_bar)

        # ── Action buttons ────────────────────────────────────────────────────
        action_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(44),
        )
        self.like_btn = MDFlatButton(
            text="🤍 J'aime",
            size_hint_x=1,
            theme_text_color="Custom",
            text_color=_hex(GRAY),
        )
        self.like_btn.bind(on_release=lambda _: self._toggle_like())

        comment_btn = MDFlatButton(
            text="💬 Commenter",
            size_hint_x=1,
            theme_text_color="Custom",
            text_color=_hex(GRAY),
        )
        comment_btn.bind(on_release=lambda _: self._open_comments())

        share_btn = MDFlatButton(
            text="📤 Partager",
            size_hint_x=1,
            theme_text_color="Custom",
            text_color=_hex(GRAY),
        )
        action_bar.add_widget(self.like_btn)
        action_bar.add_widget(comment_btn)
        action_bar.add_widget(share_btn)
        self.add_widget(action_bar)

        # Update like button state
        if self.post.get("liked_by_user"):
            self.like_btn.text = "❤️ J'aime"
            self.like_btn.text_color = _hex(PINK)

    def _react(self, emoji):
        self.post.setdefault("reactions", {})
        self.post["reactions"][emoji] = self.post["reactions"].get(emoji, 0) + 1
        count = self.post["reactions"][emoji]
        self._react_btns[emoji].text = f"{emoji} {count}"

    def _toggle_like(self):
        if self.post.get("liked_by_user"):
            self.post["likes"] = max(0, self.post.get("likes", 0) - 1)
            self.post["liked_by_user"] = False
            self.like_btn.text = "🤍 J'aime"
            self.like_btn.text_color = _hex(GRAY)
        else:
            self.post["likes"] = self.post.get("likes", 0) + 1
            self.post["liked_by_user"] = True
            self.like_btn.text = "❤️ J'aime"
            self.like_btn.text_color = _hex(PINK)
        self.controller.update_post(self.post)

    def _open_comments(self):
        comments = self.post.get("comments", [])
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        scroll = ScrollView(size_hint=(1, 0.8))
        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        inner.bind(minimum_height=inner.setter("height"))

        if not comments:
            inner.add_widget(MDLabel(
                text="Aucun commentaire. Soyez le premier ! 💬",
                halign="center",
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                size_hint_y=None, height=dp(60),
            ))
        else:
            for c in comments:
                row = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None, height=dp(52),
                    spacing=dp(8), padding=[dp(4), dp(4)],
                )
                row.add_widget(MDLabel(
                    text=c.get("avatar", "👤"),
                    font_size=dp(26),
                    size_hint=(None, None), size=(dp(36), dp(36)),
                ))
                bubble = MDBoxLayout(
                    orientation="vertical",
                    md_bg_color=_hex(LIGHT),
                )
                bubble.add_widget(MDLabel(
                    text=c.get("user", ""),
                    bold=True, font_style="Caption",
                    theme_text_color="Custom", text_color=_hex(DARK),
                    size_hint_y=None, height=dp(18),
                ))
                bubble.add_widget(MDLabel(
                    text=c.get("text", ""),
                    font_style="Caption",
                    theme_text_color="Custom", text_color=_hex(DARK),
                    size_hint_y=None, height=dp(18),
                ))
                row.add_widget(bubble)
                inner.add_widget(row)

        scroll.add_widget(inner)
        content.add_widget(scroll)

        row_input = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        inp = MDTextField(hint_text="Écrire un commentaire…",  size_hint_x=1)
        send = MDRaisedButton(
            text="▶", size_hint_x=None, width=dp(48),
            md_bg_color=_hex(PINK),
        )
        row_input.add_widget(inp)
        row_input.add_widget(send)
        content.add_widget(row_input)

        popup = Popup(title=f"💬 Commentaires",
                      content=content, size_hint=(0.95, 0.7))

        def _send(_):
            text = inp.text.strip()
            if not text:
                return
            self.post.setdefault("comments", []).append({
                "user": "Moi", "avatar": "👤",
                "text": text, "date": _time.strftime("%H:%M"),
            })
            inp.text = ""
            popup.dismiss()

        send.bind(on_release=_send)
        inp.bind(on_text_validate=_send)
        popup.open()


# ── New post dialog ───────────────────────────────────────────────────────────
def _show_new_post_dialog(on_submit):
    content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
    user = data_module.CURRENT_USER or {}
    content.add_widget(MDLabel(
        text=f"{user.get('avatar','👤')}  {user.get('name','Moi')}",
        font_style="Subtitle1", size_hint_y=None, height=dp(36),
    ))
    text_input = MDTextField(
        hint_text="Quoi de neuf ? Partagez vos cours, questions…",
        multiline=True,
        size_hint_y=None, height=dp(120),
    )
    content.add_widget(text_input)

    btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
    cancel_btn = MDFlatButton(text="Annuler", size_hint_x=1)
    post_btn = MDRaisedButton(text="📤 Publier", size_hint_x=1, md_bg_color=_hex(PINK))
    btn_row.add_widget(cancel_btn)
    btn_row.add_widget(post_btn)
    content.add_widget(btn_row)

    popup = Popup(title="Nouvelle publication",
                  content=content, size_hint=(0.92, None), height=dp(340))

    def _submit(_):
        text = text_input.text.strip()
        if not text:
            return
        popup.dismiss()
        on_submit(text)

    post_btn.bind(on_release=_submit)
    cancel_btn.bind(on_release=popup.dismiss)
    popup.open()


# ── Feed Screen ───────────────────────────────────────────────────────────────
class FeedScreen(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._build_ui()
        self.load_posts()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # ── Header ────────────────────────────────────────────────────────────
        hdr = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(52),
            padding=[dp(14), dp(8)],
            md_bg_color=(1, 1, 1, 1),
        )
        hdr.add_widget(MDLabel(
            text="📰 UniShare Feed",
            font_style="H6",
            theme_text_color="Custom",
            text_color=_hex(PINK),
        ))
        hdr.add_widget(Widget())
        self.add_widget(root)

        root.add_widget(hdr)

        # ── Create post bar ───────────────────────────────────────────────────
        user = data_module.CURRENT_USER or {}
        create_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(64),
            padding=[dp(14), dp(10)],
            spacing=dp(10),
            md_bg_color=(1, 1, 1, 1),
        )
        create_bar.add_widget(MDLabel(
            text=user.get("avatar", "👤"),
            font_size=dp(32),
            size_hint=(None, None), size=(dp(44), dp(44)),
            halign="center",
        ))
        fake_btn = MDFlatButton(
            text=f"Quoi de neuf, {user.get('name','Étudiant').split()[0]} ?",
            size_hint_x=1,
            theme_text_color="Custom",
            text_color=_hex(GRAY),
        )
        fake_btn.bind(on_release=lambda _: self._add_new_post())
        create_bar.add_widget(fake_btn)
        root.add_widget(create_bar)

        # ── Posts scroll ──────────────────────────────────────────────────────
        self.scroll = ScrollView(size_hint=(1, 1))
        self.posts_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
            padding=[0, dp(4), 0, dp(4)],
        )
        self.posts_layout.bind(minimum_height=self.posts_layout.setter("height"))
        self.scroll.add_widget(self.posts_layout)
        root.add_widget(self.scroll)

    def load_posts(self):
        self.posts_layout.clear_widgets()
        posts = self.controller.get_posts()

        if not posts:
            self.posts_layout.add_widget(MDLabel(
                text="📭 Aucune publication\n\nSoyez le premier à publier !",
                halign="center",
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                font_style="H6",
                size_hint_y=None, height=dp(200),
            ))
            return

        for post in posts:
            post.setdefault("user_avatar", "👤")
            post.setdefault("user_color", "#3498db")
            card = PostCard(post, self.controller, self)
            self.posts_layout.add_widget(card)

    def _add_new_post(self):
        def on_submit(text):
            user = data_module.CURRENT_USER or {}
            new_post = {
                "id": str(int(_time.time())),
                "user": user.get("name", "Moi"),
                "user_id": "current_user",
                "user_avatar": user.get("avatar", "👤"),
                "user_color": user.get("avatar_color", "#3498db"),
                "content": text,
                "image_path": None,
                "likes": 0,
                "liked_by_user": False,
                "comments": [],
                "reactions": {e: 0 for e in REACTIONS},
                "date": _time.strftime("%d/%m/%Y %H:%M"),
            }
            self.controller.add_post(new_post)
            self.load_posts()

        _show_new_post_dialog(on_submit)

    def refresh(self):
        self.load_posts()
