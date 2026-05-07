from PyQt5.QtWidgets import (QMainWindow, QStackedWidget, QToolBar,
                             QPushButton, QWidget, QHBoxLayout, QLabel,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from views.swipe_view import SwipeView
from views.chat_view import ChatView, ChatsView
from views.feed_view import FeedView
from views.profile_view import ProfileView
from views.marketplace_view import MarketplaceView
from controllers.swipe_controller import SwipeController
from controllers.chat_controller import ChatController
from controllers.feed_controller import FeedController
from controllers.profile_controller import ProfileController
from controllers.marketplace_controller import MarketplaceController
from utils.logo_generator import ensure_logo, get_logo_pixmap

NAV_ACTIVE   = "#1565C0"   # Blue
NAV_INACTIVE = "#607D8B"
NAV_BG       = "#FFFFFF"
NAV_HOVER    = "#E3F2FD"   # Light blue


class NavButton(QPushButton):
    def __init__(self, icon_text, label_text, parent=None):
        super().__init__(parent)
        self._icon  = icon_text
        self._label = label_text
        self.setFixedHeight(54)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self._set_style(False)

    def _set_style(self, active):
        color  = NAV_ACTIVE if active else NAV_INACTIVE
        border = f"border-bottom: 3px solid {NAV_ACTIVE};" if active else "border-bottom: 3px solid transparent;"
        self.setStyleSheet(f"""
            QPushButton {{
                background: {NAV_BG};
                border: none;
                {border}
                padding: 4px 2px 0px 2px;
                color: {color};
                font-size: 9px;
                font-weight: {'bold' if active else 'normal'};
                border-radius: 0px;
            }}
            QPushButton:hover {{ background: {NAV_HOVER}; }}
        """)
        self.setText(f"{self._icon}\n{self._label}")
        self.setFont(QFont("Segoe UI", 8))

    def setActive(self, active):
        self._set_style(active)
        self.setChecked(active)


class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.setWindowTitle("UniShare – Plateforme Étudiante Marocaine")
        self.setGeometry(100, 100, 430, 820)
        self._nav_buttons = []
        self._notif_manager = None
        ensure_logo()

        # Stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Controllers
        self.swipe_controller       = SwipeController()
        self.chat_controller        = ChatController()
        self.feed_controller        = FeedController()
        self.profile_controller     = ProfileController(current_user=current_user)
        self.marketplace_controller = MarketplaceController()

        # Views
        self.swipe_view       = SwipeView(self.swipe_controller, self)
        self.chat_view        = ChatView(self.chat_controller, self)
        self.chats_view       = ChatsView(self.chat_controller, self)
        self.feed_view        = FeedView(self.feed_controller)
        self.profile_view     = ProfileView(self.profile_controller)
        self.marketplace_view = MarketplaceView(self.marketplace_controller)

        # Give views a reference back to main_window where needed
        self.marketplace_view.set_main_window(self)
        self.profile_view.set_main_window(self)

        self.stack.addWidget(self.swipe_view)        # 0
        self.stack.addWidget(self.chat_view)         # 1
        self.stack.addWidget(self.chats_view)        # 2
        self.stack.addWidget(self.feed_view)         # 3
        self.stack.addWidget(self.profile_view)      # 4
        self.stack.addWidget(self.marketplace_view)  # 5

        # Signals
        self.swipe_view.swipe_right.connect(self.on_swipe_right)
        self.chats_view.open_chat_signal.connect(self.on_open_chat)

        # Top navigation bar
        self._create_top_nav()

        # Start notification system (after nav buttons exist)
        QTimer.singleShot(2000, self._start_notifications)

        # Default view
        self.stack.setCurrentWidget(self.swipe_view)
        self._update_nav(0)

    # ─── Navigation bar (TOP) ─────────────────────────────────────────────────

    def _create_top_nav(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background: {NAV_BG};
                border-bottom: 1px solid #E0E0E0;
                spacing: 0px; padding: 0px;
            }}
        """)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # Logo UniShare à gauche
        logo_lbl = QLabel()
        try:
            logo_pix = get_logo_pixmap(36)
            logo_lbl.setPixmap(logo_pix)
        except Exception:
            logo_lbl.setText("U")
        logo_lbl.setFixedSize(44, 54)
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("background:transparent; padding:2px;")
        row.addWidget(logo_lbl)

        defs = [
            ("🔥", "Swipe",   self.go_to_swipe),
            ("💬", "Chats",   self.go_to_chats),
            ("🛒", "Market",  self.go_to_marketplace),
            ("📰", "Feed",    self.go_to_feed),
            ("👤", "Profil",  self.go_to_profile),
        ]
        for icon, label, slot in defs:
            btn = NavButton(icon, label)
            btn.clicked.connect(slot)
            row.addWidget(btn)
            self._nav_buttons.append(btn)

        toolbar.addWidget(container)

    def _update_nav(self, active_index):
        for i, btn in enumerate(self._nav_buttons):
            btn.setActive(i == active_index)

    # ─── Notification system ──────────────────────────────────────────────────

    def _start_notifications(self):
        try:
            from views.notifications import NotificationManager
            self._notif_manager = NotificationManager(self)
        except Exception:
            pass

    def push_notification(self, message, kind="feed"):
        if self._notif_manager:
            self._notif_manager.push(message, kind)

    # ─── Navigation slots ─────────────────────────────────────────────────────

    def go_to_swipe(self):
        self.swipe_view.on_return_from_chat()
        self.stack.setCurrentWidget(self.swipe_view)
        self._update_nav(0)

    def go_to_chats(self):
        self.stack.setCurrentWidget(self.chats_view)
        self._update_nav(1)
        if self._notif_manager:
            self._notif_manager.clear_chat_badge()

    def go_to_marketplace(self):
        self.marketplace_view.load_products()
        self.stack.setCurrentWidget(self.marketplace_view)
        self._update_nav(2)

    def go_to_feed(self):
        self.stack.setCurrentWidget(self.feed_view)
        self._update_nav(3)
        if self._notif_manager:
            self._notif_manager.clear_feed_badge()

    def go_to_profile(self):
        self.profile_view.refresh()
        self.stack.setCurrentWidget(self.profile_view)
        self._update_nav(4)

    def go_back_to_chats(self):
        self.stack.setCurrentWidget(self.chats_view)
        self._update_nav(1)

    # ─── Swipe / chat signals ─────────────────────────────────────────────────

    def on_swipe_right(self, user_dict):
        self.chats_view.add_conversation(user_dict)
        self.chat_view.set_partner(user_dict)
        self.stack.setCurrentWidget(self.chat_view)
        self._update_nav(1)

    def on_open_chat(self, user_dict):
        self.chat_view.set_partner(user_dict)
        self.stack.setCurrentWidget(self.chat_view)
        self._update_nav(1)
