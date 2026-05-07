import os
import time as _time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton,
    QTextEdit, QFrame, QDialog, QMessageBox, QLineEdit, QFileDialog,
    QComboBox, QSizePolicy, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QCursor

from views.helpers import make_circle_pixmap
import utils.data as data_module

PINK   = "#1565C0"
BLUE   = "#1565C0"
DARK   = "#212121"
GRAY   = "#757575"
LIGHT  = "#E3F2FD"
WHITE  = "#FFFFFF"
GREEN  = "#43A047"

REACTIONS = ["❤️", "😂", "😮", "😢", "👍", "🔥"]
REPORT_REASONS = [
    "Contenu inapproprié", "Spam ou publicité", "Harcèlement",
    "Fausse information", "Violation des droits d'auteur", "Autre"
]


# ─── User profile mini-dialog (clic sur avatar dans le feed) ─────────────────
class UserProfileDialog(QDialog):
    def __init__(self, user_name, user_avatar, avatar_color, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setStyleSheet("background:white; border-radius:16px; border:1px solid #E0E0E0;")
        self.setFixedWidth(280)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        pix = make_circle_pixmap(user_avatar, avatar_color, 80)
        av = QLabel()
        av.setPixmap(pix)
        av.setFixedSize(80, 80)
        layout.addWidget(av, alignment=Qt.AlignCenter)

        name = QLabel(user_name)
        name.setStyleSheet(f"font-size:18px; font-weight:bold; color:{DARK};")
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        follow_btn = QPushButton("👤 Suivre")
        follow_btn.setStyleSheet(f"""
            QPushButton{{background:{PINK};color:white;border-radius:18px;
                padding:8px;font-size:13px;font-weight:bold;}}
            QPushButton:hover{{background:#1E2E4F;}}
        """)
        follow_btn.clicked.connect(self.accept)
        layout.addWidget(follow_btn)
        self.adjustSize()

    def mousePressEvent(self, e):
        self.close()


# ─── Reaction bar ─────────────────────────────────────────────────────────────
class ReactionBar(QWidget):
    """Affiche les compteurs de réactions et permet de réagir."""

    def __init__(self, post, parent=None):
        super().__init__(parent)
        self.post = post
        if "reactions" not in post:
            post["reactions"] = {e: 0 for e in REACTIONS}
        self._build()

    def _build(self):
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        self._btns = {}
        for emoji in REACTIONS:
            count = self.post["reactions"].get(emoji, 0)
            btn = QPushButton(f"{emoji} {count}" if count else emoji)
            btn.setFixedHeight(30)
            btn.setStyleSheet(f"""
                QPushButton{{background:{LIGHT};border:1px solid #E0E0E0;border-radius:14px;
                    padding:2px 10px;font-size:13px;}}
                QPushButton:hover{{background:#D9E1F1;border-color:{PINK};}}
            """)
            _e = emoji
            btn.clicked.connect(lambda _, e=_e: self._react(e))
            row.addWidget(btn)
            self._btns[emoji] = btn
        row.addStretch()

    def _react(self, emoji):
        self.post["reactions"][emoji] = self.post["reactions"].get(emoji, 0) + 1
        count = self.post["reactions"][emoji]
        self._btns[emoji].setText(f"{emoji} {count}")
        self._btns[emoji].setStyleSheet(f"""
            QPushButton{{background:#D9E1F1;border:1px solid {PINK};border-radius:14px;
                padding:2px 10px;font-size:13px;font-weight:bold;color:{PINK};}}
        """)


# ─── Comment widget (with replies) ───────────────────────────────────────────
class CommentItem(QFrame):
    def __init__(self, comment, depth=0, parent=None):
        super().__init__(parent)
        self.comment = comment
        self.depth = depth
        self.setStyleSheet("background:transparent;")

        main = QVBoxLayout(self)
        main.setContentsMargins(depth * 24, 0, 0, 0)
        main.setSpacing(4)

        # Header row
        row = QHBoxLayout()
        row.setSpacing(8)

        pix = make_circle_pixmap(
            comment.get("avatar", "👤"),
            comment.get("avatar_color", "#3498db"),
            32
        )
        av = QLabel()
        av.setPixmap(pix)
        av.setFixedSize(32, 32)
        row.addWidget(av, alignment=Qt.AlignTop)

        bubble = QFrame()
        bubble.setStyleSheet(f"background:{LIGHT};border-radius:12px;")
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(10, 8, 10, 8)
        b_layout.setSpacing(3)

        user_lbl = QLabel(comment.get("user", "Utilisateur"))
        user_lbl.setStyleSheet(f"font-size:12px; font-weight:bold; color:{DARK};")
        b_layout.addWidget(user_lbl)

        txt = QLabel(comment.get("text", ""))
        txt.setWordWrap(True)
        txt.setStyleSheet(f"font-size:13px; color:{DARK};")
        b_layout.addWidget(txt)

        row.addWidget(bubble)
        row.addStretch()
        main.addLayout(row)

        # Actions: réagir, répondre
        actions = QHBoxLayout()
        actions.setContentsMargins(40, 0, 0, 0)
        actions.setSpacing(16)

        time_lbl = QLabel(comment.get("date", ""))
        time_lbl.setStyleSheet(f"font-size:10px; color:{GRAY};")
        actions.addWidget(time_lbl)

        for react in ["❤️", "😂", "👍"]:
            rb = QPushButton(react)
            rb.setFixedSize(26, 22)
            rb.setStyleSheet("background:transparent;border:none;font-size:13px;")
            actions.addWidget(rb)

        reply_btn = QPushButton("Répondre")
        reply_btn.setStyleSheet(f"background:transparent;border:none;font-size:11px;"
                                 f"color:{GRAY};font-weight:bold;")
        reply_btn.clicked.connect(lambda: self._show_reply_input(main))
        actions.addWidget(reply_btn)
        actions.addStretch()
        main.addLayout(actions)

        # Nested replies
        for reply in comment.get("replies", []):
            main.addWidget(CommentItem(reply, depth + 1))

        self._reply_box_shown = False
        self._main_layout = main

    def _show_reply_input(self, layout):
        if self._reply_box_shown:
            return
        self._reply_box_shown = True
        reply_row = QHBoxLayout()
        reply_row.setContentsMargins(40, 0, 0, 0)
        inp = QLineEdit()
        inp.setPlaceholderText("Répondre…")
        inp.setStyleSheet(f"border:1px solid #E0E0E0;border-radius:14px;padding:6px 12px;font-size:13px;")
        send = QPushButton("↩")
        send.setFixedSize(32, 32)
        send.setStyleSheet(f"background:{PINK};color:white;border-radius:16px;font-size:14px;")

        def _do_reply():
            text = inp.text().strip()
            if text:
                self.comment.setdefault("replies", []).append({
                    "user": "Moi",
                    "avatar": "👤",
                    "avatar_color": "#3498db",
                    "text": text,
                    "date": _time.strftime("%H:%M"),
                    "replies": [],
                })
                reply_widget = CommentItem(self.comment["replies"][-1], self.depth + 1)
                layout.addWidget(reply_widget)
                inp.clear()

        send.clicked.connect(_do_reply)
        inp.returnPressed.connect(_do_reply)
        reply_row.addWidget(inp)
        reply_row.addWidget(send)
        layout.addLayout(reply_row)


# ─── Comments dialog ──────────────────────────────────────────────────────────
class CommentsDialog(QDialog):
    def __init__(self, post, parent=None):
        super().__init__(parent)
        self.post = post
        self.setWindowTitle(f"Commentaires · {post['user']}")
        self.setGeometry(60, 80, 400, 560)
        self.setStyleSheet("background:white;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title
        hdr = QLabel(f"💬 Commentaires ({len(self.post.get('comments', []))})")
        hdr.setStyleSheet(f"font-size:17px;font-weight:bold;color:{DARK};"
                           "padding:14px 16px; border-bottom:1px solid #E0E0E0;")
        layout.addWidget(hdr)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        self._content = QWidget()
        self._c_layout = QVBoxLayout(self._content)
        self._c_layout.setContentsMargins(12, 12, 12, 12)
        self._c_layout.setSpacing(10)
        self._c_layout.setAlignment(Qt.AlignTop)
        self._render_comments()
        scroll.setWidget(self._content)
        layout.addWidget(scroll, stretch=1)

        # Add comment
        add_bar = QFrame()
        add_bar.setStyleSheet("border-top:1px solid #E0E0E0; background:white;")
        ab = QHBoxLayout(add_bar)
        ab.setContentsMargins(12, 10, 12, 10)
        ab.setSpacing(8)
        self._new_inp = QLineEdit()
        self._new_inp.setPlaceholderText("Écrire un commentaire…")
        self._new_inp.setStyleSheet(f"border:1px solid #E0E0E0;border-radius:18px;"
                                     "padding:8px 14px;font-size:13px;")
        self._new_inp.returnPressed.connect(self._add_comment)
        send_btn = QPushButton("▶")
        send_btn.setFixedSize(38, 38)
        send_btn.setStyleSheet(f"background:{PINK};color:white;border-radius:19px;font-size:16px;")
        send_btn.clicked.connect(self._add_comment)
        ab.addWidget(self._new_inp)
        ab.addWidget(send_btn)
        layout.addWidget(add_bar)

    def _render_comments(self):
        while self._c_layout.count():
            item = self._c_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        comments = self.post.get("comments", [])
        if not comments:
            empty = QLabel("Aucun commentaire. Soyez le premier ! 💬")
            empty.setStyleSheet(f"color:{GRAY};font-size:13px;padding:20px;")
            empty.setAlignment(Qt.AlignCenter)
            self._c_layout.addWidget(empty)
        else:
            for c in comments:
                self._c_layout.addWidget(CommentItem(c))

    def _add_comment(self):
        text = self._new_inp.text().strip()
        if not text:
            return
        comment = {
            "user": "Moi",
            "avatar": "👤",
            "avatar_color": "#3498db",
            "text": text,
            "date": _time.strftime("%H:%M"),
            "replies": [],
        }
        self.post.setdefault("comments", []).append(comment)
        self._new_inp.clear()
        self._render_comments()


# ─── Add post dialog ─────────────────────────────────────────────────────────
class AddPostDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle publication")
        self.setGeometry(60, 120, 400, 420)
        self.setStyleSheet("background:white;")
        self.selected_image = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        user = data_module.CURRENT_USER or {}
        pix = make_circle_pixmap(
            user.get("avatar", "👤"),
            user.get("avatar_color", "#3498db"),
            42,
            user.get("photo_path")
        )
        av = QLabel()
        av.setPixmap(pix)
        av.setFixedSize(42, 42)
        layout.addWidget(av)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Quoi de neuf ? Partagez vos cours, questions…")
        self.text_input.setStyleSheet(f"border:none;font-size:15px;color:{DARK};")
        self.text_input.setMinimumHeight(120)
        layout.addWidget(self.text_input)

        # Image
        self._img_preview = QLabel()
        self._img_preview.setAlignment(Qt.AlignCenter)
        self._img_preview.hide()
        layout.addWidget(self._img_preview)

        tools = QHBoxLayout()
        img_btn = QPushButton("🖼️ Photo")
        img_btn.setStyleSheet(f"background:{LIGHT};border:1px solid #E0E0E0;border-radius:12px;"
                               "padding:8px 14px;font-size:13px;")
        img_btn.clicked.connect(self._pick_image)
        tools.addWidget(img_btn)
        tools.addStretch()

        post_btn = QPushButton("📤 Publier")
        post_btn.setStyleSheet(f"background:{PINK};color:white;border-radius:18px;"
                                "padding:10px 24px;font-size:14px;font-weight:bold;")
        post_btn.clicked.connect(self._submit)
        tools.addWidget(post_btn)
        layout.addLayout(tools)

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self.selected_image = path
            pix = QPixmap(path).scaled(360, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._img_preview.setPixmap(pix)
            self._img_preview.show()

    def _submit(self):
        text = self.text_input.toPlainText().strip()
        if not text and not self.selected_image:
            QMessageBox.warning(self, "Vide", "Écrivez quelque chose ou ajoutez une image.")
            return
        self.accept()

    def get_data(self):
        return self.text_input.toPlainText().strip(), self.selected_image


# ─── Post widget (Facebook-like) ─────────────────────────────────────────────
class PostWidget(QFrame):
    def __init__(self, post, controller, feed_view, parent=None):
        super().__init__(parent)
        self.post = post
        self.controller = controller
        self.feed_view = feed_view
        self.setStyleSheet(f"""
            QFrame{{background:{WHITE};border-bottom:8px solid {LIGHT};}}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ──
        hdr = QWidget()
        hdr.setStyleSheet("background:white;")
        h_row = QHBoxLayout(hdr)
        h_row.setContentsMargins(14, 12, 14, 8)
        h_row.setSpacing(10)

        pix = make_circle_pixmap(
            self.post.get("user_avatar", "👤"),
            self.post.get("user_color", "#3498db"),
            44
        )
        av_lbl = QLabel()
        av_lbl.setPixmap(pix)
        av_lbl.setFixedSize(44, 44)
        av_lbl.setCursor(Qt.PointingHandCursor)
        av_lbl.mousePressEvent = lambda e: self._open_user_profile()
        h_row.addWidget(av_lbl)

        info = QVBoxLayout()
        info.setSpacing(1)
        name_lbl = QLabel(self.post.get("user", ""))
        name_lbl.setStyleSheet(f"font-size:14px;font-weight:bold;color:{DARK};")
        name_lbl.setCursor(Qt.PointingHandCursor)
        name_lbl.mousePressEvent = lambda e: self._open_user_profile()
        info.addWidget(name_lbl)
        date_lbl = QLabel(self.post.get("date", ""))
        date_lbl.setStyleSheet(f"font-size:11px;color:{GRAY};")
        info.addWidget(date_lbl)
        h_row.addLayout(info)
        h_row.addStretch()

        # Options menu
        opts_btn = QPushButton("•••")
        opts_btn.setFixedSize(34, 34)
        opts_btn.setStyleSheet(f"background:transparent;border:none;font-size:16px;color:{GRAY};")
        opts_btn.clicked.connect(self._show_options)
        h_row.addWidget(opts_btn)

        layout.addWidget(hdr)

        # ── Content ──
        content_txt = self.post.get("content", "")
        if content_txt:
            c_lbl = QLabel(content_txt)
            c_lbl.setWordWrap(True)
            c_lbl.setStyleSheet(f"font-size:14px;color:{DARK};padding:4px 14px 8px 14px;")
            layout.addWidget(c_lbl)

        # ── Image ──
        img_path = self.post.get("image_path")
        if img_path and os.path.exists(img_path):
            pix_img = QPixmap(img_path).scaledToWidth(430, Qt.SmoothTransformation)
            img_lbl = QLabel()
            img_lbl.setPixmap(pix_img)
            img_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(img_lbl)

        # ── Stats ──
        stats_bar = QWidget()
        stats_bar.setStyleSheet("background:white; border-top:1px solid #F0F0F0;")
        s_row = QHBoxLayout(stats_bar)
        s_row.setContentsMargins(14, 6, 14, 6)
        s_row.setSpacing(6)

        likes = self.post.get("likes", 0)
        total_reactions = sum(self.post.get("reactions", {}).values())
        stats_txt = ""
        if likes or total_reactions:
            stats_txt += f"❤️ {likes + total_reactions}"
        comments_count = len(self.post.get("comments", []))
        if comments_count:
            stats_txt += f"  💬 {comments_count}"

        stats_lbl = QLabel(stats_txt)
        stats_lbl.setStyleSheet(f"font-size:12px;color:{GRAY};")
        s_row.addWidget(stats_lbl)
        s_row.addStretch()
        layout.addWidget(stats_bar)

        # ── Reactions bar ──
        react_bar = QWidget()
        react_bar.setStyleSheet(f"background:white; border-top:1px solid #F0F0F0;"
                                  " padding:4px 10px;")
        react_layout = QHBoxLayout(react_bar)
        react_layout.setContentsMargins(10, 4, 10, 4)
        react_layout.setSpacing(4)
        self._react_widget = ReactionBar(self.post)
        react_layout.addWidget(self._react_widget)
        layout.addWidget(react_bar)

        # ── Action buttons (Like, Comment, Share) ──
        action_bar = QWidget()
        action_bar.setStyleSheet(f"background:white; border-top:1px solid #F0F0F0;")
        a_row = QHBoxLayout(action_bar)
        a_row.setContentsMargins(0, 0, 0, 0)
        a_row.setSpacing(0)

        self.like_btn = self._action_btn(
            f"{'❤️' if self.post.get('liked_by_user') else '🤍'} J'aime",
            PINK if self.post.get("liked_by_user") else GRAY
        )
        self.like_btn.clicked.connect(self._toggle_like)

        comment_btn = self._action_btn("💬 Commenter", GRAY)
        comment_btn.clicked.connect(self._open_comments)

        share_btn = self._action_btn("📤 Partager", GRAY)
        share_btn.clicked.connect(self._share_post)

        a_row.addWidget(self.like_btn)
        a_row.addWidget(comment_btn)
        a_row.addWidget(share_btn)
        layout.addWidget(action_bar)

    @staticmethod
    def _action_btn(text, color):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton{{background:transparent;border:none;font-size:13px;
                font-weight:bold;color:{color};padding:10px 4px;}}
            QPushButton:hover{{background:{LIGHT};}}
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

    def _toggle_like(self):
        if self.post.get("liked_by_user"):
            self.post["likes"] = max(0, self.post["likes"] - 1)
            self.post["liked_by_user"] = False
            self.like_btn.setText("🤍 J'aime")
            self.like_btn.setStyleSheet(self.like_btn.styleSheet().replace(PINK, GRAY))
        else:
            self.post["likes"] += 1
            self.post["liked_by_user"] = True
            self.like_btn.setText("❤️ J'aime")
            self.like_btn.setStyleSheet(self.like_btn.styleSheet().replace(GRAY, PINK))
        self.controller.update_post(self.post)

    def _open_comments(self):
        dlg = CommentsDialog(self.post, self)
        dlg.exec_()

    def _share_post(self):
        from PyQt5.QtWidgets import QApplication
        link = f"unishare://post/{self.post.get('id', '?')}"
        QApplication.clipboard().setText(link)
        QMessageBox.information(self, "Partagé", f"Lien copié :\n{link}")

    def _open_user_profile(self):
        dlg = UserProfileDialog(
            self.post.get("user", ""),
            self.post.get("user_avatar", "👤"),
            self.post.get("user_color", "#3498db"),
            self
        )
        dlg.move(QCursor.pos())
        dlg.exec_()

    def _show_options(self):
        menu = QMenu(self)
        is_mine = self.post.get("user_id") == "current_user"
        if is_mine:
            del_action = QAction("🗑️ Supprimer", self)
            del_action.triggered.connect(self._delete_post)
            menu.addAction(del_action)
        else:
            report_action = QAction("⚠️ Signaler", self)
            report_action.triggered.connect(self._report_post)
            menu.addAction(report_action)
        menu.exec_(QCursor.pos())

    def _delete_post(self):
        reply = QMessageBox.question(self, "Supprimer",
                                     "Supprimer cette publication ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_post(self.post)
            self.deleteLater()

    def _report_post(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Signaler")
        dlg.setStyleSheet("background:white;")
        dlg.setFixedSize(360, 260)
        vb = QVBoxLayout(dlg)
        vb.setContentsMargins(20, 20, 20, 20)
        vb.setSpacing(12)
        vb.addWidget(QLabel("⚠️ Motif du signalement :"))
        combo = QComboBox()
        combo.addItems(REPORT_REASONS)
        combo.setStyleSheet("padding:8px;border-radius:8px;border:1px solid #E0E0E0;")
        vb.addWidget(combo)
        confirm = QPushButton("Signaler")
        confirm.setStyleSheet(f"background:#D32F2F;color:white;border-radius:16px;padding:10px;")
        confirm.clicked.connect(dlg.accept)
        vb.addWidget(confirm)
        if dlg.exec_():
            QMessageBox.information(self, "Signalé", "Merci. Notre équipe va examiner.")


# ─── Feed View ────────────────────────────────────────────────────────────────
class FeedView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet(f"background:{LIGHT};")
        self._build_ui()
        self.load_posts()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        hdr = QFrame()
        hdr.setStyleSheet("background:white; border-bottom:1px solid #E0E0E0;")
        hdr.setFixedHeight(52)
        h_row = QHBoxLayout(hdr)
        h_row.setContentsMargins(14, 8, 14, 8)

        logo = QLabel("📰 UniShare Feed")
        logo.setStyleSheet(f"font-size:18px; font-weight:bold; color:{BLUE};")
        h_row.addWidget(logo)
        h_row.addStretch()

        self._notif_btn = QPushButton("🔔")
        self._notif_btn.setFixedSize(38, 38)
        self._notif_btn.setStyleSheet(
            "background:transparent;border:none;font-size:20px;"
            "QPushButton:hover{background:#F5F5F5;border-radius:19px;}")
        self._notif_btn.clicked.connect(self._open_notif_panel)
        h_row.addWidget(self._notif_btn)

        layout.addWidget(hdr)

        # Create post bar
        create_bar = QFrame()
        create_bar.setStyleSheet("background:white; border-bottom:8px solid #F5F5F5;")
        c_row = QHBoxLayout(create_bar)
        c_row.setContentsMargins(14, 10, 14, 10)
        c_row.setSpacing(10)

        user = data_module.CURRENT_USER or {}
        pix = make_circle_pixmap(
            user.get("avatar", "👤"),
            user.get("avatar_color", "#3498db"),
            42,
            user.get("photo_path")
        )
        av = QLabel()
        av.setPixmap(pix)
        av.setFixedSize(42, 42)
        c_row.addWidget(av)

        fake_input = QPushButton(f"Quoi de neuf, {user.get('name', 'Étudiant').split()[0]} ?")
        fake_input.setStyleSheet(f"""
            QPushButton{{background:{LIGHT};border:1px solid #E0E0E0;border-radius:22px;
                padding:10px 16px;font-size:14px;color:{GRAY};text-align:left;}}
            QPushButton:hover{{background:#D9E1F1;border-color:{PINK};}}
        """)
        fake_input.clicked.connect(self._add_new_post)
        c_row.addWidget(fake_input)

        layout.addWidget(create_bar)

        # Posts scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none; background:#F5F5F5;")

        self.posts_content = QWidget()
        self.posts_content.setStyleSheet("background:#F5F5F5;")
        self.posts_layout = QVBoxLayout(self.posts_content)
        self.posts_layout.setContentsMargins(0, 0, 0, 0)
        self.posts_layout.setSpacing(0)
        self.posts_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.posts_content)
        layout.addWidget(self.scroll, stretch=1)

    def load_posts(self):
        while self.posts_layout.count():
            item = self.posts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        posts = self.controller.get_posts()
        if not posts:
            empty = QLabel("📭 Aucune publication\n\nSoyez le premier à publier !")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"padding:60px; color:{GRAY}; font-size:15px;")
            self.posts_layout.addWidget(empty)
            return

        for post in posts:
            if "user_avatar" not in post:
                post["user_avatar"] = "👤"
            if "user_color" not in post:
                post["user_color"] = "#3498db"
            widget = PostWidget(post, self.controller, self)
            self.posts_layout.addWidget(widget)

    def _add_new_post(self):
        dlg = AddPostDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            text, img_path = dlg.get_data()
            user = data_module.CURRENT_USER or {}
            new_post = {
                "id": str(int(_time.time())),
                "user": user.get("name", "Moi"),
                "user_id": "current_user",
                "user_avatar": user.get("avatar", "👤"),
                "user_color": user.get("avatar_color", "#3498db"),
                "content": text,
                "image_path": img_path,
                "likes": 0,
                "liked_by_user": False,
                "comments": [],
                "reactions": {e: 0 for e in REACTIONS},
                "date": _time.strftime("%d/%m/%Y %H:%M"),
            }
            self.controller.add_post(new_post)
            # Notification
            try:
                data_module.NOTIFICATIONS.append({
                    "type": "post",
                    "text": f"📰 {user.get('name','Moi')} a publié : {text[:40]}…",
                    "read": False,
                })
            except Exception:
                pass
            self.load_posts()

    def _open_notif_panel(self):
        """Ouvre le panneau de notifications."""
        try:
            from views.notifications import NotificationPanel
            panel = NotificationPanel(self)
            # Position sous le bouton cloche
            pos = self._notif_btn.mapTo(self, self._notif_btn.rect().bottomLeft())
            panel.move(max(0, pos.x() - panel.width() + self._notif_btn.width()), pos.y() + 2)
            panel.show()
        except Exception:
            pass

    def refresh(self):
        self.load_posts()
