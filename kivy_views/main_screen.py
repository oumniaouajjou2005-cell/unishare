from kivy.metrics import dp
from kivy.utils import get_color_from_hex

from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

from controllers.swipe_controller import SwipeController
from controllers.chat_controller import ChatController
from controllers.feed_controller import FeedController
from controllers.profile_controller import ProfileController
from controllers.marketplace_controller import MarketplaceController


def _hex(h):
    return get_color_from_hex(h)


class MainScreen(MDScreen):
    def __init__(self, current_user=None, **kwargs):
        super().__init__(**kwargs)
        self.current_user = current_user

        # Controllers (identiques à la version PyQt5)
        self.swipe_controller       = SwipeController()
        self.chat_controller        = ChatController()
        self.feed_controller        = FeedController()
        self.profile_controller     = ProfileController(current_user=current_user)
        self.marketplace_controller = MarketplaceController()

        self._build_ui()

    def _build_ui(self):
        nav = MDBottomNavigation(
            panel_color=_hex("#FFFFFF"),
            selected_color_background=_hex("#E3F2FD"),
            text_color_active=_hex("#1565C0"),
            text_color_normal=_hex("#607D8B"),
        )

        # ── 1. Swipe ──────────────────────────────────────────────────────────
        swipe_item = MDBottomNavigationItem(name="swipe", text="Swipe", icon="fire")
        from kivy_views.swipe_screen import SwipeScreen
        self.swipe_screen = SwipeScreen(
            controller=self.swipe_controller,
            main_screen=self,
        )
        swipe_item.add_widget(self.swipe_screen)
        nav.add_widget(swipe_item)

        # ── 2. Chats ──────────────────────────────────────────────────────────
        chat_item = MDBottomNavigationItem(name="chats", text="Chats", icon="message")
        from kivy_views.chat_screen import ChatsScreen
        self.chats_screen = ChatsScreen(
            controller=self.chat_controller,
            main_screen=self,
        )
        chat_item.add_widget(self.chats_screen)
        nav.add_widget(chat_item)

        # ── 3. Marketplace ────────────────────────────────────────────────────
        market_item = MDBottomNavigationItem(name="market", text="Market", icon="cart")
        from kivy_views.marketplace_screen import MarketplaceScreen
        self.marketplace_screen = MarketplaceScreen(
            controller=self.marketplace_controller,
        )
        market_item.add_widget(self.marketplace_screen)
        nav.add_widget(market_item)

        # ── 4. Feed ───────────────────────────────────────────────────────────
        feed_item = MDBottomNavigationItem(name="feed", text="Feed", icon="newspaper")
        from kivy_views.feed_screen import FeedScreen
        self.feed_screen = FeedScreen(
            controller=self.feed_controller,
        )
        feed_item.add_widget(self.feed_screen)
        nav.add_widget(feed_item)

        # ── 5. Profil ─────────────────────────────────────────────────────────
        profile_item = MDBottomNavigationItem(name="profile", text="Profil", icon="account")
        from kivy_views.profile_screen import ProfileScreen
        self.profile_screen = ProfileScreen(
            controller=self.profile_controller,
            main_screen=self,
        )
        profile_item.add_widget(self.profile_screen)
        nav.add_widget(profile_item)

        self.add_widget(nav)
        self._nav = nav

    # ── Navigation helpers (appelés par les sous-écrans) ─────────────────────

    def go_to_chat_with(self, user_dict):
        from kivy_views.chat_screen import ChatScreen
        if not hasattr(self, '_chat_screen'):
            self._chat_screen = ChatScreen(controller=self.chat_controller, main_screen=self)
            chat_item = self._nav.ids.get("chats")

        self.chats_screen.add_conversation(user_dict)
        self.chats_screen.open_chat(user_dict)
        self._nav.switch_tab("chats")

    def go_to_chats(self):
        self._nav.switch_tab("chats")

    def go_to_swipe(self):
        self._nav.switch_tab("swipe")
