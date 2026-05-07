"""
Système de notifications UniShare.
- NotificationToast   : bannière qui glisse en haut de l'écran
- BadgeLabel          : pastille numérotée sur les boutons nav
- NotificationPanel   : liste des notifications
- NotificationManager : orchestrateur, vérifie Firebase toutes les 30 s
"""
import time as _time
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QLabel,
                              QPushButton, QWidget, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QPoint

import utils.data as data_module

PINK  = "#1565C0"
DARK  = "#212121"
GRAY  = "#757575"
WHITE = "#FFFFFF"
LIGHT = "#F5F5F5"
GREEN = "#43A047"
RED   = "#E53935"


# ─── Toast ────────────────────────────────────────────────────────────────────
class NotificationToast(QFrame):
    def __init__(self, message, icon="🔔", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("QFrame{background:rgba(33,33,33,0.93);border-radius:14px;}")
        self.setFixedWidth(min(390, (parent.width() - 20) if parent else 370))

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(10)

        ic = QLabel(icon)
        ic.setStyleSheet("font-size:20px;background:transparent;color:white;")
        row.addWidget(ic)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color:white;font-size:13px;background:transparent;")
        row.addWidget(msg_lbl, stretch=1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setStyleSheet(
            "QPushButton{background:transparent;color:rgba(255,255,255,0.55);"
            "border:none;font-size:13px;}"
            "QPushButton:hover{color:white;}")
        close_btn.clicked.connect(self.hide)
        row.addWidget(close_btn)

        self.adjustSize()
        QTimer.singleShot(4800, self.hide)

    @classmethod
    def show_in(cls, message, parent_widget, icon="🔔"):
        if not parent_widget:
            return
        toast = cls(message, icon, parent_widget)
        pw = parent_widget.width()
        x  = max(8, (pw - toast.width()) // 2)
        toast.move(x, 68)
        toast.raise_()
        toast.show()


# ─── Badge ────────────────────────────────────────────────────────────────────
class BadgeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._count = 0
        self.setFixedSize(17, 17)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"background:{PINK};color:white;border-radius:8px;"
            "font-size:10px;font-weight:bold;")
        self.hide()

    def set_count(self, n):
        self._count = max(0, n)
        if self._count:
            self.setText(str(min(self._count, 99)))
            self.show()
            self.raise_()
        else:
            self.hide()

    def increment(self):
        self.set_count(self._count + 1)

    def reset(self):
        self.set_count(0)


# ─── Follow Request Row ───────────────────────────────────────────────────────
class FollowRequestRow(QFrame):
    def __init__(self, request, on_accept, on_reject, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#EEF7FF;border-radius:10px;margin:4px 8px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        name  = request.get("from_name", "Quelqu'un")
        school = request.get("from_school", "")

        info = QLabel(f"👤 <b>{name}</b> veut vous suivre")
        info.setStyleSheet(f"font-size:13px;color:{DARK};")
        info.setWordWrap(True)
        layout.addWidget(info)

        if school:
            sub = QLabel(school)
            sub.setStyleSheet(f"font-size:11px;color:{GRAY};")
            layout.addWidget(sub)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        accept_btn = QPushButton("✓ Accepter")
        accept_btn.setStyleSheet(
            f"background:{GREEN};color:white;border-radius:8px;"
            "padding:6px 12px;font-weight:bold;border:none;font-size:12px;")
        accept_btn.clicked.connect(lambda: on_accept(request))

        reject_btn = QPushButton("✕ Refuser")
        reject_btn.setStyleSheet(
            f"background:#FFEBEE;color:{RED};border-radius:8px;"
            "padding:6px 12px;font-weight:bold;border:none;font-size:12px;")
        reject_btn.clicked.connect(lambda: on_reject(request))

        btns.addWidget(accept_btn)
        btns.addWidget(reject_btn)
        layout.addLayout(btns)


# ─── Notification Panel ───────────────────────────────────────────────────────
class NotificationPanel(QFrame):
    def __init__(self, follow_requests=None, on_accept=None, on_reject=None, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setStyleSheet(
            "QFrame{background:white;border-radius:16px;border:1px solid #E0E0E0;}")
        self.setFixedWidth(320)
        self._follow_requests = follow_requests or {}
        self._on_accept = on_accept
        self._on_reject = on_reject
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.setContentsMargins(14, 12, 14, 12)
        title = QLabel("🔔 Notifications")
        title.setStyleSheet(f"font-size:15px;font-weight:bold;color:{DARK};")
        hdr.addWidget(title)
        hdr.addStretch()
        clear = QPushButton("Tout lire")
        clear.setStyleSheet(f"background:transparent;border:none;color:{PINK};"
                             "font-size:12px;font-weight:bold;")
        clear.clicked.connect(self._mark_all_read)
        hdr.addWidget(clear)

        hdr_w = QWidget()
        hdr_w.setStyleSheet("border-bottom:1px solid #F0F0F0;")
        hdr_w.setLayout(hdr)
        layout.addWidget(hdr_w)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        scroll.setFixedHeight(360)

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 4, 0, 4)
        self._list_layout.setSpacing(2)
        self._list_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll)
        self._refresh_list()
        self.adjustSize()

    def _refresh_list(self):
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        has_content = False

        # Demandes de suivi en attente
        for from_uid, req in self._follow_requests.items():
            row = FollowRequestRow(req, self._on_accept, self._on_reject, self)
            self._list_layout.addWidget(row)
            has_content = True

        # Notifications générales
        notifs = getattr(data_module, "NOTIFICATIONS", [])
        for notif in reversed(notifs[-20:]):
            is_unread = not notif.get("read", False)
            row = QFrame()
            row.setStyleSheet(
                f"background:{'#F0F7FF' if is_unread else WHITE};"
                "border-bottom:1px solid #F5F5F5;")
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(14, 10, 14, 10)
            r_layout.setSpacing(8)

            icon_map = {"chat": "💬", "post": "📰", "market": "🛒",
                        "follow": "👤", "info": "ℹ️"}
            icon_lbl = QLabel(icon_map.get(notif.get("type", "info"), "🔔"))
            icon_lbl.setStyleSheet("font-size:18px;")
            r_layout.addWidget(icon_lbl)

            txt_col = QVBoxLayout()
            txt = QLabel(notif.get("text", ""))
            txt.setWordWrap(True)
            txt.setStyleSheet(f"font-size:12px;color:{DARK};"
                               f"{'font-weight:bold;' if is_unread else ''}")
            txt_col.addWidget(txt)
            ts = QLabel(notif.get("time", ""))
            ts.setStyleSheet(f"font-size:10px;color:{GRAY};")
            txt_col.addWidget(ts)
            r_layout.addLayout(txt_col)

            if is_unread:
                dot = QLabel("●")
                dot.setStyleSheet(f"color:{PINK};font-size:10px;min-width:10px;")
                r_layout.addWidget(dot)
                notif["read"] = True

            self._list_layout.addWidget(row)
            has_content = True

        if not has_content:
            empty = QLabel("Aucune notification pour le moment")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color:{GRAY};font-size:13px;padding:30px;")
            self._list_layout.addWidget(empty)

    def showEvent(self, event):
        self._refresh_list()
        super().showEvent(event)

    def _mark_all_read(self):
        for n in getattr(data_module, "NOTIFICATIONS", []):
            n["read"] = True
        self._refresh_list()


# ─── Notification Manager ─────────────────────────────────────────────────────
class NotificationManager:
    def __init__(self, main_window):
        self.mw            = main_window
        self._chat_badge   = None
        self._feed_badge   = None
        self._market_badge = None
        self._notif_badge  = None
        self._panel        = None
        self._seen_requests = set()

        QTimer.singleShot(300, self._attach_badges)

        # Vérifier les follow requests toutes les 30 s
        self._follow_timer = QTimer()
        self._follow_timer.timeout.connect(self._check_follow_requests)
        self._follow_timer.start(30_000)

    # ── Badges ────────────────────────────────────────────────────────────────

    def _attach_badges(self):
        nav = getattr(self.mw, "_nav_buttons", [])
        if len(nav) >= 5:
            self._chat_badge   = self._make_badge(nav[1])
            self._feed_badge   = self._make_badge(nav[3])
            self._market_badge = self._make_badge(nav[2])

    @staticmethod
    def _make_badge(btn):
        badge = BadgeLabel(btn)
        badge.move(btn.width() - 18, 3)
        return badge

    # ── Push ──────────────────────────────────────────────────────────────────

    def push(self, message, kind="feed", icon="🔔"):
        data_module.NOTIFICATIONS.append({
            "type": kind,
            "text": message,
            "time": _time.strftime("%H:%M"),
            "read": False,
        })
        NotificationToast.show_in(message, self.mw, icon)
        badge = {"chat":   self._chat_badge,
                 "feed":   self._feed_badge,
                 "market": self._market_badge}.get(kind)
        if badge:
            badge.increment()

    def clear_badge(self, kind):
        badge = {"chat":   self._chat_badge,
                 "feed":   self._feed_badge,
                 "market": self._market_badge}.get(kind)
        if badge:
            badge.reset()

    def clear_chat_badge(self):   self.clear_badge("chat")
    def clear_feed_badge(self):   self.clear_badge("feed")
    def clear_market_badge(self): self.clear_badge("market")

    def open_panel(self, anchor_widget):
        if self._panel:
            try:
                self._panel.close()
            except Exception:
                pass
        requests = dict(data_module.FOLLOW_REQUESTS)
        self._panel = NotificationPanel(
            follow_requests=requests,
            on_accept=self._accept_follow,
            on_reject=self._reject_follow,
        )
        pos = anchor_widget.mapToGlobal(QPoint(0, anchor_widget.height()))
        self._panel.move(pos)
        self._panel.show()

    # ── Follow requests ───────────────────────────────────────────────────────

    def _check_follow_requests(self):
        try:
            from utils import api_client
            user = data_module.CURRENT_USER or {}
            uid  = user.get("id", "")
            if not uid:
                return
            requests = api_client.get_follow_requests(uid)
            data_module.FOLLOW_REQUESTS = requests

            for from_uid, req in requests.items():
                if from_uid not in self._seen_requests:
                    self._seen_requests.add(from_uid)
                    name = req.get("from_name", "Quelqu'un")
                    self.push(
                        f"👤 {name} veut vous suivre – ouvrez les notifications pour répondre.",
                        "feed", "👤")
        except Exception:
            pass

    def _accept_follow(self, request):
        try:
            from utils import api_client
            user    = data_module.CURRENT_USER or {}
            to_uid  = user.get("id", "")
            from_uid = request.get("from_id", "")
            if to_uid and from_uid:
                api_client.accept_follow(from_uid, to_uid)
                data_module.FOLLOW_REQUESTS.pop(from_uid, None)
                name = request.get("from_name", "")
                self.push(f"✅ Vous suivez maintenant {name}.", "follow", "✅")
                if self._panel:
                    try:
                        self._panel.close()
                    except Exception:
                        pass
        except Exception:
            pass

    def _reject_follow(self, request):
        try:
            from utils import api_client
            user     = data_module.CURRENT_USER or {}
            to_uid   = user.get("id", "")
            from_uid = request.get("from_id", "")
            if to_uid and from_uid:
                api_client.reject_follow(from_uid, to_uid)
                data_module.FOLLOW_REQUESTS.pop(from_uid, None)
                if self._panel:
                    try:
                        self._panel.close()
                    except Exception:
                        pass
        except Exception:
            pass
