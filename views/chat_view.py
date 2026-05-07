import random
import time as _time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QDialog, QMessageBox, QSizePolicy, QListWidget,
    QListWidgetItem, QMenu, QAction
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QFont, QCursor

from views.helpers import make_circle_pixmap

PINK    = "#1565C0"
BLUE_BG = "#1565C0"   # bulles envoyées
GRAY_BG = "#EEEEEE"   # bulles reçues
DARK    = "#212121"
GRAY    = "#757575"
WHITE   = "#FFFFFF"
LIGHT   = "#E3F2FD"

EMOJI_REACTIONS = ["❤️", "😂", "😮", "😢", "👍", "🔥"]

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


# ─── Emoji picker ─────────────────────────────────────────────────────────────
class EmojiPickerPopup(QDialog):
    emoji_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setStyleSheet("background:white; border-radius:16px; border:1px solid #E0E0E0;")
        row = QHBoxLayout(self)
        row.setContentsMargins(8, 8, 8, 8)
        row.setSpacing(4)
        for emoji in EMOJI_REACTIONS:
            btn = QPushButton(emoji)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton{background:transparent;border:none;font-size:22px;border-radius:8px;}
                QPushButton:hover{background:#D9E1F1;}
            """)
            btn.clicked.connect(lambda _, e=emoji: self._pick(e))
            row.addWidget(btn)
        self.adjustSize()

    def _pick(self, emoji):
        self.emoji_selected.emit(emoji)
        self.close()


# ─── Message bubble widget ────────────────────────────────────────────────────
class MessageBubble(QFrame):
    def __init__(self, msg, is_mine, partner_pix=None, parent=None):
        super().__init__(parent)
        self.msg = msg
        self.is_mine = is_mine
        self.reaction_lbl = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_ctx_menu)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(8, 3, 8, 3)
        outer.setSpacing(8)

        if is_mine:
            outer.addStretch()
        else:
            if partner_pix:
                av = QLabel()
                av.setPixmap(partner_pix)
                av.setFixedSize(34, 34)
                outer.addWidget(av, alignment=Qt.AlignBottom)

        bubble = QFrame()
        bubble.setMaximumWidth(270)
        if is_mine:
            bubble.setStyleSheet(f"""
                QFrame{{background:{BLUE_BG};border-radius:18px 18px 4px 18px;
                    padding:10px 14px;}}
            """)
        elif msg.get("sender") == "system":
            bubble.setStyleSheet("""
                QFrame{background:#F3E5F5;border-radius:12px;padding:8px 14px;}
            """)
        else:
            bubble.setStyleSheet(f"""
                QFrame{{background:{GRAY_BG};border-radius:18px 18px 18px 4px;
                    padding:10px 14px;}}
            """)

        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(4)

        text_color = "white" if is_mine else DARK
        if msg.get("sender") == "system":
            text_color = "#6A1B9A"

        txt = QLabel(msg["text"])
        txt.setWordWrap(True)
        txt.setStyleSheet(f"color:{text_color}; font-size:14px; background:transparent;")
        b_layout.addWidget(txt)

        time_str = msg.get("time", "")
        if time_str:
            t_lbl = QLabel(time_str)
            t_lbl.setStyleSheet(f"color:{'rgba(255,255,255,0.65)' if is_mine else GRAY};"
                                 " font-size:10px; background:transparent;")
            t_lbl.setAlignment(Qt.AlignRight if is_mine else Qt.AlignLeft)
            b_layout.addWidget(t_lbl)

        # Reaction label (populated later)
        self.reaction_lbl = QLabel("")
        self.reaction_lbl.setStyleSheet(f"font-size:16px; background:transparent; color:{DARK};")
        self.reaction_lbl.hide()
        b_layout.addWidget(self.reaction_lbl)

        outer.addWidget(bubble)
        if not is_mine:
            outer.addStretch()

    def _show_ctx_menu(self, pos):
        menu = QMenu(self)
        react_action = QAction("😀 Réagir", self)
        react_action.triggered.connect(self._show_emoji_picker)
        menu.addAction(react_action)
        menu.exec_(QCursor.pos())

    def _show_emoji_picker(self):
        picker = EmojiPickerPopup(self)
        picker.emoji_selected.connect(self._apply_reaction)
        picker.move(QCursor.pos())
        picker.exec_()

    def _apply_reaction(self, emoji):
        self.reaction_lbl.setText(emoji)
        self.reaction_lbl.show()


# ─── Chat View ────────────────────────────────────────────────────────────────
class ChatView(QWidget):
    def __init__(self, controller, main_window):
        super().__init__()
        self.controller = controller
        self.main_window = main_window
        self.current_partner = None
        self.messages = []
        self._partner_pix = None
        self.setStyleSheet(f"background:{LIGHT};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self._header = QFrame()
        self._header.setStyleSheet(f"""
            QFrame{{background:white; border-bottom:1px solid #E0E0E0;}}
        """)
        self._header.setFixedHeight(62)
        h_row = QHBoxLayout(self._header)
        h_row.setContentsMargins(8, 8, 8, 8)
        h_row.setSpacing(10)

        back_btn = QPushButton("←")
        back_btn.setFixedSize(38, 38)
        back_btn.setStyleSheet(f"""
            QPushButton{{background:transparent;border:none;font-size:22px;color:{DARK};}}
            QPushButton:hover{{color:{PINK};}}
        """)
        back_btn.clicked.connect(self._go_back)
        h_row.addWidget(back_btn)

        self._partner_av_lbl = QLabel()
        self._partner_av_lbl.setFixedSize(42, 42)
        h_row.addWidget(self._partner_av_lbl)

        self._partner_name_lbl = QLabel("Conversation")
        self._partner_name_lbl.setStyleSheet(f"font-size:16px; font-weight:bold; color:{DARK};")
        h_row.addWidget(self._partner_name_lbl)

        self._online_dot = QLabel("🟢 En ligne")
        self._online_dot.setStyleSheet(f"font-size:10px; color:{GRAY};")
        h_row.addWidget(self._online_dot)

        h_row.addStretch()

        report_btn = QPushButton("⚠️")
        report_btn.setFixedSize(36, 36)
        report_btn.setToolTip("Signaler")
        report_btn.setStyleSheet(f"""
            QPushButton{{background:transparent;border:none;font-size:18px;}}
            QPushButton:hover{{color:#D32F2F;}}
        """)
        report_btn.clicked.connect(self._report_user)
        h_row.addWidget(report_btn)

        layout.addWidget(self._header)

        # Messages scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("border:none; background:#F5F5F5;")

        self._messages_widget = QWidget()
        self._messages_widget.setStyleSheet("background:#F5F5F5;")
        self._msg_layout = QVBoxLayout(self._messages_widget)
        self._msg_layout.setContentsMargins(0, 8, 0, 8)
        self._msg_layout.setSpacing(4)
        self._msg_layout.addStretch()

        self._scroll.setWidget(self._messages_widget)
        layout.addWidget(self._scroll, stretch=1)

        # Input bar
        input_bar = QFrame()
        input_bar.setStyleSheet("background:white; border-top:1px solid #E0E0E0;")
        input_bar.setFixedHeight(64)
        in_row = QHBoxLayout(input_bar)
        in_row.setContentsMargins(12, 10, 12, 10)
        in_row.setSpacing(10)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Aa  Écrire un message…")
        self._input.setStyleSheet(f"""
            QLineEdit{{background:{LIGHT};border:none;border-radius:22px;
                padding:10px 16px;font-size:14px;}}
        """)
        self._input.returnPressed.connect(self._send_message)
        in_row.addWidget(self._input)

        send_btn = QPushButton("▶")
        send_btn.setFixedSize(44, 44)
        send_btn.setStyleSheet(f"""
            QPushButton{{background:{PINK};color:white;border-radius:22px;font-size:18px;}}
            QPushButton:hover{{background:#1E2E4F;}}
        """)
        send_btn.clicked.connect(self._send_message)
        in_row.addWidget(send_btn)

        layout.addWidget(input_bar)

    def set_partner(self, user_dict):
        self.current_partner = user_dict
        self._partner_pix = make_circle_pixmap(
            user_dict.get("avatar", "👤"),
            user_dict.get("avatar_color", "#3498db"),
            42,
            user_dict.get("photo_path")
        )
        self._partner_av_lbl.setPixmap(self._partner_pix)
        self._partner_name_lbl.setText(user_dict["name"])

        self.messages = [
            {"sender": "system",
             "text": f"🤝 Vous matchez avec {user_dict['name']} ! Commencez à discuter.",
             "time": ""},
        ]
        self._refresh_messages()

    def _send_message(self):
        text = self._input.text().strip()
        if not text or not self.current_partner:
            return
        self.messages.append({
            "sender": "moi",
            "text": text,
            "time": _time.strftime("%H:%M")
        })
        self._refresh_messages()
        self._input.clear()

        # Notification + auto-reply
        import utils.data as data_module
        if hasattr(data_module, "add_notification"):
            pass  # handled by notification system

        QTimer.singleShot(1200 + random.randint(0, 800), self._auto_reply)

    def _auto_reply(self):
        if not self.current_partner:
            return
        reply = random.choice(AUTO_REPLIES)
        self.messages.append({
            "sender": self.current_partner["name"],
            "text": reply,
            "time": _time.strftime("%H:%M")
        })
        self._refresh_messages()

        # Push notification
        try:
            import utils.data as data_module
            data_module.NOTIFICATIONS.append({
                "type": "chat",
                "text": f"💬 {self.current_partner['name']}: {reply[:40]}",
                "read": False,
            })
        except Exception:
            pass

    def _refresh_messages(self):
        # Remove all except the stretch at index 0
        while self._msg_layout.count() > 1:
            item = self._msg_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        partner_sm_pix = make_circle_pixmap(
            self.current_partner.get("avatar", "👤") if self.current_partner else "👤",
            self.current_partner.get("avatar_color", "#3498db") if self.current_partner else "#3498db",
            34,
            self.current_partner.get("photo_path") if self.current_partner else None
        ) if self.current_partner else None

        for msg in self.messages:
            is_mine = msg["sender"] == "moi"
            is_system = msg["sender"] == "system"
            bubble = MessageBubble(msg, is_mine,
                                   None if (is_mine or is_system) else partner_sm_pix,
                                   self)
            self._msg_layout.addWidget(bubble)

        QTimer.singleShot(50, self._scroll_bottom)

    def _scroll_bottom(self):
        vsb = self._scroll.verticalScrollBar()
        vsb.setValue(vsb.maximum())

    def _go_back(self):
        self.main_window.go_back_to_chats()

    def _report_user(self):
        if not self.current_partner:
            return
        reply = QMessageBox.question(
            self, "Signalement",
            f"Signaler {self.current_partner['name']} pour comportement inapproprié ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self, "Signalement envoyé",
                "Merci. Notre équipe va examiner ce cas."
            )


# ─── Chats List View ──────────────────────────────────────────────────────────
class ChatsView(QWidget):
    open_chat_signal = pyqtSignal(dict)

    def __init__(self, controller, main_window):
        super().__init__()
        self.controller = controller
        self.main_window = main_window
        self.conversations = []
        self.setStyleSheet(f"background:{LIGHT};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background:white; border-bottom:1px solid #E0E0E0;")
        header.setFixedHeight(56)
        h_row = QHBoxLayout(header)
        h_row.setContentsMargins(16, 8, 16, 8)

        title = QLabel("💬 Messages")
        title.setStyleSheet(f"font-size:20px; font-weight:bold; color:{DARK};")
        h_row.addWidget(title)
        h_row.addStretch()

        layout.addWidget(header)

        # Conversations scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("border:none; background:#F5F5F5;")

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background:#F5F5F5;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 8, 0, 8)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_widget)
        layout.addWidget(self._scroll, stretch=1)

        # Empty state
        self._empty_lbl = QLabel(
            "📭 Aucune conversation\n\nSwipe à droite sur un profil\npour commencer à chatter !"
        )
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setStyleSheet(f"color:{GRAY}; font-size:14px; padding:60px;")
        layout.addWidget(self._empty_lbl)

        self._update_empty_state()

    def add_conversation(self, user):
        if any(u["id"] == user["id"] for u in self.conversations):
            return
        self.conversations.append(user)
        self._add_row(user)
        self._update_empty_state()

    def _add_row(self, user):
        # Remove stretch first
        stretch_item = self._list_layout.takeAt(self._list_layout.count() - 1)

        row = QFrame()
        row.setStyleSheet("""
            QFrame{background:white;border-bottom:1px solid #F0F0F0;}
            QFrame:hover{background:#D9E1F1;}
        """)
        row.setFixedHeight(72)
        row.setCursor(Qt.PointingHandCursor)

        r_layout = QHBoxLayout(row)
        r_layout.setContentsMargins(14, 10, 14, 10)
        r_layout.setSpacing(12)

        pix = make_circle_pixmap(
            user.get("avatar", "👤"),
            user.get("avatar_color", "#3498db"),
            50,
            user.get("photo_path")
        )
        av = QLabel()
        av.setPixmap(pix)
        av.setFixedSize(50, 50)
        r_layout.addWidget(av)

        info = QVBoxLayout()
        info.setSpacing(3)
        name = QLabel(user["name"])
        name.setStyleSheet(f"font-size:15px; font-weight:bold; color:{DARK};")
        sub = QLabel(user.get("school", ""))
        sub.setStyleSheet(f"font-size:12px; color:{GRAY};")
        info.addWidget(name)
        info.addWidget(sub)
        r_layout.addLayout(info)
        r_layout.addStretch()

        online = QLabel("🟢")
        online.setStyleSheet("font-size:12px;")
        r_layout.addWidget(online)

        _user = user
        row.mousePressEvent = lambda e, u=_user: self.open_chat_signal.emit(u)

        self._list_layout.addWidget(row)
        self._list_layout.addStretch()

    def _update_empty_state(self):
        has = len(self.conversations) > 0
        self._scroll.setVisible(has)
        self._empty_lbl.setVisible(not has)

    def showEvent(self, event):
        self._update_empty_state()
        super().showEvent(event)
