from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGraphicsDropShadowEffect, QPushButton,
                             QDialog, QListWidget, QListWidgetItem, QFrame,
                             QScrollArea, QSizePolicy)
from PyQt5.QtCore import (pyqtSignal, Qt, QPoint, QPointF,
                          QPropertyAnimation, QEasingCurve, QTimer,
                          QRect)
from PyQt5.QtGui import (QColor, QPixmap, QPainter, QPainterPath,
                          QBrush, QLinearGradient, QPen, QFont,
                          QTransform)

from views.helpers import make_circle_pixmap

PINK    = "#1565C0"
GREEN   = "#43A047"
YELLOW  = "#F9A825"
DARK    = "#212121"
GRAY    = "#757575"
LIGHT   = "#E3F2FD"
WHITE   = "#FFFFFF"
NOPE_COLOR = "#E53935"


# ─── Toast ───────────────────────────────────────────────────────────────────
class ToastNotification(QFrame):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        lbl = QLabel(message)
        lbl.setStyleSheet("color:white; font-size:13px; font-weight:bold;")
        layout.addWidget(lbl)
        self.setStyleSheet("QFrame{background:rgba(33,33,33,0.90);border-radius:25px;}")
        self.adjustSize()
        if parent:
            pr = parent.rect()
            self.move(pr.center().x() - self.width() // 2, pr.height() - 100)
        QTimer.singleShot(2500, self.close)


# ─── Match popup ─────────────────────────────────────────────────────────────
class MatchPopup(QWidget):
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        if parent:
            self.setFixedSize(parent.width(), parent.height())

        overlay = QFrame(self)
        overlay.setStyleSheet("QFrame{background:rgba(0,0,0,0.60); border-radius:0px;}")
        overlay.setGeometry(0, 0, self.width() or 430, self.height() or 700)

        box = QFrame(self)
        box.setFixedWidth(320)
        box.setStyleSheet("""
            QFrame{background:white; border-radius:24px; padding:0px;}
        """)
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(28, 30, 28, 28)
        box_layout.setSpacing(14)
        box_layout.setAlignment(Qt.AlignHCenter)

        heart = QLabel("🤝")
        heart.setStyleSheet("font-size:56px; background:transparent;")
        heart.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(heart)

        match_lbl = QLabel("C'est un Match !")
        match_lbl.setStyleSheet(f"font-size:22px; font-weight:bold; color:{PINK}; background:transparent;")
        match_lbl.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(match_lbl)

        sub = QLabel(f"Toi et {user['name']} vous êtes matchés !\nCommencez à discuter 💬")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size:13px; color:{GRAY}; background:transparent;")
        box_layout.addWidget(sub)

        avatars_row = QHBoxLayout()
        avatars_row.setAlignment(Qt.AlignCenter)
        avatars_row.setSpacing(16)

        me_pix = make_circle_pixmap("👤", "#3498db", 64)
        me_lbl = QLabel()
        me_lbl.setPixmap(me_pix)
        me_lbl.setFixedSize(64, 64)
        avatars_row.addWidget(me_lbl)

        them_pix = make_circle_pixmap(
            user.get("avatar", "👤"),
            user.get("avatar_color", "#e91e63"),
            64,
            user.get("photo_path")
        )
        them_lbl = QLabel()
        them_lbl.setPixmap(them_pix)
        them_lbl.setFixedSize(64, 64)
        avatars_row.addWidget(them_lbl)
        box_layout.addLayout(avatars_row)

        btn_chat = QPushButton("💬 Envoyer un message")
        btn_chat.setStyleSheet(f"""
            QPushButton{{background:{PINK};color:white;border-radius:22px;
                padding:12px;font-size:14px;font-weight:bold;}}
            QPushButton:hover{{background:#1E2E4F;}}
        """)
        btn_chat.clicked.connect(self._on_yes)
        box_layout.addWidget(btn_chat)

        btn_later = QPushButton("Plus tard")
        btn_later.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{GRAY};border:none;
                font-size:13px;padding:6px;}}
            QPushButton:hover{{color:{DARK};}}
        """)
        btn_later.clicked.connect(self._on_no)
        box_layout.addWidget(btn_later)

        box.adjustSize()
        box.move(
            (self.width() or 430) // 2 - box.width() // 2,
            (self.height() or 700) // 2 - box.height() // 2
        )
        overlay.raise_()
        box.raise_()

    def showEvent(self, e):
        if self.parent():
            self.resize(self.parent().width(), self.parent().height())
        super().showEvent(e)

    def _on_yes(self):
        self.confirmed.emit()
        self.close()

    def _on_no(self):
        self.cancelled.emit()
        self.close()


# ─── Profile dialog ──────────────────────────────────────────────────────────
class ProfileDetailDialog(QDialog):
    def __init__(self, user, parent_view, parent=None):
        super().__init__(parent)
        self.user = user
        self.parent_view = parent_view
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background:#F5F5F5;")
        self.setGeometry(40, 80, 350, 560)
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        scroll.setGeometry(0, 0, 350, 560)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 20)

        # Photo header
        header = QFrame()
        header.setFixedHeight(240)
        header.setStyleSheet(f"background:{self.user.get('avatar_color','#3498db')};"
                              "border-bottom-left-radius:24px; border-bottom-right-radius:24px;")
        h_layout = QVBoxLayout(header)
        h_layout.setAlignment(Qt.AlignCenter)

        pix = make_circle_pixmap(
            self.user.get("avatar", "👤"),
            self.user.get("avatar_color", "#3498db"),
            120,
            self.user.get("photo_path")
        )
        photo_lbl = QLabel()
        photo_lbl.setPixmap(pix)
        photo_lbl.setFixedSize(120, 120)
        photo_lbl.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(photo_lbl, alignment=Qt.AlignCenter)

        name_lbl = QLabel(f"{self.user['name']}, {self.user.get('age','')}")
        name_lbl.setStyleSheet("color:white; font-size:22px; font-weight:bold; background:transparent;")
        name_lbl.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(name_lbl)

        layout.addWidget(header)

        # Info card
        info_card = QFrame()
        info_card.setStyleSheet("background:white; border-radius:16px; margin:0 12px;")
        ic_layout = QVBoxLayout(info_card)
        ic_layout.setContentsMargins(16, 14, 16, 14)
        ic_layout.setSpacing(8)

        for icon, text in [("🏫", self.user.get("school", "")),
                            ("📖", self.user.get("major", ""))]:
            lbl = QLabel(f"{icon}  {text}")
            lbl.setStyleSheet(f"font-size:14px; color:{DARK};")
            ic_layout.addWidget(lbl)

        layout.addWidget(info_card)

        # Bio card
        if self.user.get("bio"):
            bio_card = QFrame()
            bio_card.setStyleSheet("background:white; border-radius:16px; margin:0 12px;")
            bl = QVBoxLayout(bio_card)
            bl.setContentsMargins(16, 14, 16, 14)
            bio_title = QLabel("📝 Bio")
            bio_title.setStyleSheet(f"font-weight:bold; font-size:14px; color:{DARK};")
            bl.addWidget(bio_title)
            bio_txt = QLabel(self.user.get("bio", ""))
            bio_txt.setWordWrap(True)
            bio_txt.setStyleSheet(f"font-size:13px; color:{GRAY};")
            bl.addWidget(bio_txt)
            layout.addWidget(bio_card)

        # Chat button
        chat_btn = QPushButton(f"💬 Chatter avec {self.user['name']}")
        chat_btn.setStyleSheet(f"""
            QPushButton{{background:{PINK};color:white;border-radius:22px;
                padding:14px;font-size:15px;font-weight:bold;margin:0 12px;}}
            QPushButton:hover{{background:#1E2E4F;}}
        """)
        chat_btn.clicked.connect(self._on_chat)
        layout.addWidget(chat_btn)

        scroll.setWidget(content)

    def _on_chat(self):
        self.close()
        self.parent_view.start_chat_direct(self.user)

    def mousePressEvent(self, event):
        self.close()


# ─── Swipe Card (style Tinder) ───────────────────────────────────────────────
class SwipeCard(QWidget):
    CARD_W = 330
    CARD_H = 510

    def __init__(self, user_data, controller, parent_view):
        super().__init__()
        self.user = user_data
        self.controller = controller
        self.parent_view = parent_view

        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:transparent;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        # Overlay labels (LIKE / NOPE)
        self._like_lbl = QLabel("LIKE", self)
        self._like_lbl.setStyleSheet("""
            color: #43A047; font-size: 34px; font-weight: bold;
            border: 4px solid #43A047; border-radius: 8px;
            padding: 4px 12px; background: transparent;
        """)
        self._like_lbl.setGeometry(20, 50, 130, 60)
        self._like_lbl.hide()

        self._nope_lbl = QLabel("NOPE", self)
        self._nope_lbl.setStyleSheet("""
            color: #E91E63; font-size: 34px; font-weight: bold;
            border: 4px solid #E91E63; border-radius: 8px;
            padding: 4px 12px; background: transparent;
        """)
        self._nope_lbl.setGeometry(self.CARD_W - 150, 50, 130, 60)
        self._nope_lbl.hide()

        # Drag state
        self.dragging = False
        self.drag_start = QPointF()
        self.start_pos = QPoint()
        self.swipe_completed = False

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(280)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    # ─── Paint (Tinder-like card) ─────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        W, H = self.CARD_W, self.CARD_H
        PHOTO_H = int(H * 0.72)
        RADIUS = 22

        # Card shape clip
        clip = QPainterPath()
        clip.addRoundedRect(0, 0, W, H, RADIUS, RADIUS)
        p.setClipPath(clip)

        # ── Photo / avatar background ──
        color = self.user.get("avatar_color", "#3498db")
        photo_path = self.user.get("photo_path")

        if photo_path:
            import os
            src = QPixmap(photo_path)
            if not src.isNull():
                src = src.scaled(W, PHOTO_H, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                ox = (src.width() - W) // 2
                oy = (src.height() - PHOTO_H) // 2
                p.drawPixmap(0, 0, src, ox, oy, W, PHOTO_H)
            else:
                self._draw_avatar_bg(p, W, PHOTO_H, color)
        else:
            self._draw_avatar_bg(p, W, PHOTO_H, color)

        # ── Gradient overlay on photo (bottom half) ──
        grad = QLinearGradient(0, PHOTO_H - 120, 0, PHOTO_H)
        grad.setColorAt(0, QColor(0, 0, 0, 0))
        grad.setColorAt(1, QColor(0, 0, 0, 180))
        p.fillRect(0, PHOTO_H - 120, W, 120, QBrush(grad))

        # ── Name + age on photo ──
        p.setClipping(False)
        p.setPen(QColor("white"))
        font = QFont("Segoe UI", 20, QFont.Bold)
        p.setFont(font)
        name_text = f"{self.user.get('name', '')}, {self.user.get('age', '')}"
        p.drawText(QRect(16, PHOTO_H - 60, W - 32, 44),
                   Qt.AlignLeft | Qt.AlignVCenter, name_text)

        # ── School small text ──
        font2 = QFont("Segoe UI", 11)
        p.setFont(font2)
        p.setPen(QColor(220, 220, 220))
        p.drawText(QRect(16, PHOTO_H - 22, W - 32, 22),
                   Qt.AlignLeft | Qt.AlignVCenter,
                   f"🏫 {self.user.get('school', '')}")

        # ── Bottom info panel ──
        p.setClipPath(clip)
        p.fillRect(0, PHOTO_H, W, H - PHOTO_H, QBrush(QColor("white")))

        # Major pill
        p.setClipping(False)
        pill_text = f"📖 {self.user.get('major', '')}"
        font3 = QFont("Segoe UI", 11, QFont.Bold)
        p.setFont(font3)
        fm = p.fontMetrics()
        pill_w = fm.width(pill_text) + 24
        pill_x = 16
        pill_y = PHOTO_H + 10
        pill_h = 28
        pill_path = QPainterPath()
        pill_path.addRoundedRect(pill_x, pill_y, pill_w, pill_h, 14, 14)
        p.fillPath(pill_path, QBrush(QColor("#D9E1F1")))
        p.setPen(QColor(PINK))
        p.drawText(QRect(pill_x, pill_y, pill_w, pill_h), Qt.AlignCenter, pill_text)

        # Bio snippet
        bio = self.user.get("bio", "")[:70]
        if len(self.user.get("bio", "")) > 70:
            bio += "…"
        font4 = QFont("Segoe UI", 11)
        p.setFont(font4)
        p.setPen(QColor(GRAY))
        p.drawText(QRect(16, PHOTO_H + 48, W - 32, 48),
                   Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, bio)

        p.end()

    def _draw_avatar_bg(self, p, W, PHOTO_H, color):
        grad = QLinearGradient(0, 0, W, PHOTO_H)
        grad.setColorAt(0, QColor(color).lighter(150))
        grad.setColorAt(1, QColor(color))
        p.fillRect(0, 0, W, PHOTO_H, QBrush(grad))
        # Big emoji centered
        font = QFont()
        font.setPointSize(90)
        p.setFont(font)
        p.setPen(Qt.NoPen)
        p.drawText(QRect(0, 20, W, PHOTO_H - 80), Qt.AlignCenter,
                   self.user.get("avatar", "👤"))

    # ─── Swipe actions ────────────────────────────────────────────────────────

    def swipe_left(self):
        if self.swipe_completed:
            return
        self.swipe_completed = True
        self._nope_lbl.hide()
        self._like_lbl.hide()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(-self.CARD_W - 100, self.pos().y()))
        self.animation.finished.connect(self._close_card)
        self.animation.start()

    def swipe_right(self):
        if self.swipe_completed:
            return
        self.swipe_completed = True
        self._nope_lbl.hide()
        self._like_lbl.hide()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(self.CARD_W + 500, self.pos().y()))
        self.animation.finished.connect(self._after_right)
        self.animation.start()

    def swipe_down(self):
        if self.swipe_completed:
            return
        self.swipe_completed = True
        self._nope_lbl.hide()
        self._like_lbl.hide()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(self.pos().x(), self.pos().y() + 600))
        self.animation.finished.connect(self._close_card)
        self.animation.start()
        self.parent_view.save_for_later(self.user, show_popup=True)

    def _close_card(self):
        self.deleteLater()
        self.parent_view.load_next_card()

    def _after_right(self):
        self.deleteLater()
        self.parent_view.after_swipe_right(self.user)

    # ─── Mouse events (drag + tilt) ───────────────────────────────────────────

    def mousePressEvent(self, event):
        if self.swipe_completed:
            return
        self.dragging = True
        self.drag_start = event.pos()
        self.start_pos = self.pos()
        event.accept()

    def mouseMoveEvent(self, event):
        if not self.dragging or self.swipe_completed:
            return
        dx = event.x() - self.drag_start.x()
        dy = event.y() - self.drag_start.y()
        self.move(self.start_pos.x() + dx, self.start_pos.y() + dy)

        # Rotation
        angle = dx * 0.08
        transform = QTransform().rotate(angle)
        self.setGraphicsEffect(None)  # remove shadow during drag for perf
        # Show LIKE / NOPE overlays
        if dx > 30:
            self._like_lbl.show()
            self._nope_lbl.hide()
            alpha = min(int(abs(dx) / 120 * 255), 200)
            self._like_lbl.setStyleSheet(f"""
                color: rgba(67,160,71,{alpha}); font-size: 34px; font-weight: bold;
                border: 4px solid rgba(67,160,71,{alpha}); border-radius: 8px;
                padding: 4px 12px; background: transparent;
            """)
        elif dx < -30:
            self._nope_lbl.show()
            self._like_lbl.hide()
            alpha = min(int(abs(dx) / 120 * 255), 200)
            self._nope_lbl.setStyleSheet(f"""
                color: rgba(233,30,99,{alpha}); font-size: 34px; font-weight: bold;
                border: 4px solid rgba(233,30,99,{alpha}); border-radius: 8px;
                padding: 4px 12px; background: transparent;
            """)
        else:
            self._like_lbl.hide()
            self._nope_lbl.hide()
        event.accept()

    def mouseReleaseEvent(self, event):
        if not self.dragging or self.swipe_completed:
            return
        self.dragging = False
        self._like_lbl.hide()
        self._nope_lbl.hide()
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        dx = self.x() - self.start_pos.x()
        dy = self.y() - self.start_pos.y()

        if abs(dx) > 70 or abs(dy) > 70:
            if abs(dx) >= abs(dy):
                if dx > 70:
                    self.swipe_right()
                else:
                    self.swipe_left()
            else:
                if dy > 70:
                    self.swipe_down()
                else:
                    self._return_to_start()
        else:
            # Tap → show profile detail
            if abs(dx) < 10 and abs(dy) < 10:
                self._return_to_start()
                dlg = ProfileDetailDialog(self.user, self.parent_view, self.parent_view)
                dlg.show()
            else:
                self._return_to_start()
        event.accept()

    def _return_to_start(self):
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.start_pos)
        self.animation.start()


# ─── SwipeView ───────────────────────────────────────────────────────────────
class SwipeView(QWidget):
    swipe_right = pyqtSignal(dict)

    def __init__(self, controller, main_window):
        super().__init__()
        self.controller = controller
        self.main_window = main_window
        self.current_index = 0
        self.current_users = []
        self.toast = None
        self.current_popup = None
        self.pending_user = None
        self.setStyleSheet("background:#F5F5F5;")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Titre bar
        top_bar = QWidget()
        top_bar.setStyleSheet("background:white; border-bottom:1px solid #E0E0E0;")
        top_bar.setFixedHeight(48)
        top_row = QHBoxLayout(top_bar)
        top_row.setContentsMargins(16, 0, 16, 0)
        top_row.setSpacing(8)

        logo = QLabel("🎓 UniShare")
        logo.setStyleSheet(f"font-size:18px; font-weight:bold; color:{PINK};")
        top_row.addWidget(logo)
        top_row.addStretch()

        self.later_btn = QPushButton("⏰ Plus tard")
        self.later_btn.setStyleSheet(f"""
            QPushButton{{background:{YELLOW};color:white;border-radius:14px;
                padding:5px 12px;font-size:12px;font-weight:bold;}}
            QPushButton:hover{{background:#F57F17;}}
        """)
        self.later_btn.clicked.connect(self._show_saved)
        top_row.addWidget(self.later_btn)

        layout.addWidget(top_bar)

        # Indicators row
        ind_bar = QWidget()
        ind_bar.setStyleSheet("background:#F5F5F5;")
        ind_row = QHBoxLayout(ind_bar)
        ind_row.setContentsMargins(20, 6, 20, 6)
        for txt, color in [("✗ Passer", PINK), ("⏰ Plus tard", YELLOW), ("🤝 Match", GREEN)]:
            lbl = QLabel(txt)
            lbl.setStyleSheet(f"color:{color}; font-size:11px; font-weight:bold;")
            ind_row.addWidget(lbl, alignment=Qt.AlignCenter)
        layout.addWidget(ind_bar)

        # Card container
        self.card_container = QWidget()
        self.card_container.setStyleSheet("background:transparent;")
        self.card_layout = QHBoxLayout(self.card_container)
        self.card_layout.setAlignment(Qt.AlignCenter)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.card_container, stretch=1)

        # Action buttons (Tinder style circles)
        btn_bar = QWidget()
        btn_bar.setStyleSheet("background:#F5F5F5;")
        btn_bar.setFixedHeight(100)
        btn_row = QHBoxLayout(btn_bar)
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(20)
        btn_row.setContentsMargins(30, 10, 30, 10)

        self.btn_nope = self._make_action_btn("✗", "#FFEBEE", NOPE_COLOR, 60)
        self.btn_later_action = self._make_action_btn("⏰", "#FFF9C4", YELLOW, 50)
        self.btn_like = self._make_action_btn("🤝", "#E8F5E9", GREEN, 60)

        self.btn_nope.clicked.connect(self._on_nope)
        self.btn_later_action.clicked.connect(self._on_later)
        self.btn_like.clicked.connect(self._on_like)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_nope)
        btn_row.addWidget(self.btn_later_action)
        btn_row.addWidget(self.btn_like)
        btn_row.addStretch()
        layout.addWidget(btn_bar)

        # Status label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"color:{GRAY}; font-size:11px; padding:4px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.refresh_users()

    @staticmethod
    def _make_action_btn(icon, bg, border, size):
        btn = QPushButton(icon)
        btn.setFixedSize(size, size)
        btn.setStyleSheet(f"""
            QPushButton{{
                background:{bg}; border:2px solid {border};
                border-radius:{size//2}px; font-size:{size//3}px;
            }}
            QPushButton:hover{{background:{border}; color:white;}}
        """)
        return btn

    # ─── Card logic ───────────────────────────────────────────────────────────

    def _current_card(self):
        for i in range(self.card_layout.count()):
            w = self.card_layout.itemAt(i).widget()
            if isinstance(w, SwipeCard):
                return w
        return None

    def _on_nope(self):
        card = self._current_card()
        if card:
            card.swipe_left()

    def _on_like(self):
        card = self._current_card()
        if card:
            card.swipe_right()

    def _on_later(self):
        card = self._current_card()
        if card:
            card.swipe_down()

    def refresh_users(self):
        self.current_users = self.controller.get_users_to_swipe()
        self.current_index = 0
        self.load_next_card()

    def load_next_card(self):
        for i in reversed(range(self.card_layout.count())):
            w = self.card_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

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
        self.card_layout.addWidget(card)
        self.current_index += 1

        remaining = len(self.current_users) - self.current_index % len(self.current_users)
        self.info_label.setText(f"👥 {remaining} profil(s) à découvrir • Glisse ou clique !")

    def _show_empty(self):
        empty = QLabel("🎉 Plus de profils !\nReviens bientôt…")
        empty.setStyleSheet(f"""
            font-size:16px; color:{GRAY}; padding:60px;
            background:white; border-radius:24px;
        """)
        empty.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(empty)
        self.info_label.setText("")

    def after_swipe_right(self, user):
        import utils.data as data_module
        current = data_module.CURRENT_USER or {}
        try:
            from utils import api_client
            api_client.send_follow_request(current, user.get("id", ""))
        except Exception:
            pass
        name = user.get("name", "")
        self._show_toast(f"📨 Demande de suivi envoyée à {name}")
        self.load_next_card()

    def start_chat_direct(self, user):
        self.main_window.chats_view.add_conversation(user)
        self.swipe_right.emit(user)

    def save_for_later(self, user, show_popup=False):
        already = self.controller.is_saved_for_later(user["id"])
        if not already:
            self.controller.save_for_later(user)
            if show_popup:
                self._show_toast(f"✅ {user['name']} ajouté à Plus tard")
        else:
            # Popup visible (pas seulement toast) quand déjà enregistré
            self._show_already_saved_popup(user)

    def _show_already_saved_popup(self, user):
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Déjà sauvegardé")
        msg.setText(f"📌 {user['name']} est déjà dans ta liste « Plus tard » !")
        msg.setInformativeText("Tu peux le retrouver dans ton Profil → Voir Plus Tard.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def _show_toast(self, message):
        if self.toast:
            try:
                self.toast.close()
            except Exception:
                pass
        self.toast = ToastNotification(message, self)
        self.toast.show()

    def _show_saved(self):
        later_users = self.controller.get_later_users()
        if not later_users:
            self._show_toast("📭 Aucun profil sauvegardé")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Profils sauvegardés")
        dialog.setGeometry(40, 80, 360, 480)
        dialog.setStyleSheet("background:white;")
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("⏰ Profils sauvegardés")
        title.setStyleSheet(f"font-size:18px; font-weight:bold; color:{DARK};")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        sc_content = QWidget()
        sc_layout = QVBoxLayout(sc_content)
        sc_layout.setSpacing(10)

        for user in later_users:
            row = QFrame()
            row.setStyleSheet("background:#F5F5F5; border-radius:14px; padding:8px;")
            rl = QHBoxLayout(row)
            rl.setSpacing(12)

            pix = make_circle_pixmap(
                user.get("avatar", "👤"),
                user.get("avatar_color", "#3498db"),
                50,
                user.get("photo_path")
            )
            av = QLabel()
            av.setPixmap(pix)
            av.setFixedSize(50, 50)
            rl.addWidget(av)

            info = QVBoxLayout()
            n = QLabel(f"{user['name']}, {user.get('age', '')}")
            n.setStyleSheet(f"font-weight:bold; font-size:14px; color:{DARK};")
            s = QLabel(user.get("school", ""))
            s.setStyleSheet(f"font-size:12px; color:{GRAY};")
            info.addWidget(n)
            info.addWidget(s)
            rl.addLayout(info)
            rl.addStretch()

            view_btn = QPushButton("Voir")
            view_btn.setStyleSheet(f"""
                QPushButton{{background:{PINK};color:white;border-radius:12px;
                    padding:6px 14px;font-size:12px;}}
                QPushButton:hover{{background:#1E2E4F;}}
            """)
            _user = user
            view_btn.clicked.connect(lambda _, u=_user: [dialog.accept(),
                                                          self._view_saved_profile(u)])
            rl.addWidget(view_btn)
            sc_layout.addWidget(row)

        scroll.setWidget(sc_content)
        layout.addWidget(scroll)
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet(f"""
            QPushButton{{background:{PINK};color:white;border-radius:18px;padding:10px;}}
            QPushButton:hover{{background:#1E2E4F;}}
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec_()

    def _view_saved_profile(self, user):
        dlg = ProfileDetailDialog(user, self, self)
        dlg.show()

    def on_return_from_chat(self):
        self.refresh_users()
