import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp

import utils.data as data_module

Window.size = (430, 820)


class UniShareApp(MDApp):
    def build(self):
        self.title = "UniShare – Plateforme Étudiante Marocaine"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "800"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"

        self._init_firebase()
        self._init_server()

        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))

        from kivy_views.login_screen import LoginScreen
        login = LoginScreen(name="login")
        login.on_login_success = self._on_login
        self.sm.add_widget(login)

        saved = self._try_auto_login()
        if saved:
            data_module.CURRENT_USER = saved
            self._launch_main(saved)
            self.sm.current = "main"

        return self.sm

    # ── Init helpers ──────────────────────────────────────────────────────────

    def _init_firebase(self):
        try:
            from utils import firebase_client as fb
            fb.load_config()
            if fb.is_configured():
                data_module.APP_SETTINGS["firebase_enabled"] = True
                data_module.APP_SETTINGS["server_running"] = True
            else:
                data_module.APP_SETTINGS["firebase_enabled"] = False
        except Exception:
            pass

    def _init_server(self):
        try:
            from utils.network_server import start_server
            from utils import api_client
            ok, ip, port = start_server(8765)
            api_client.set_server_url(f"http://127.0.0.1:{port}")
            data_module.APP_SETTINGS["server_ip"] = ip
            data_module.APP_SETTINGS["server_port"] = port
            if not data_module.APP_SETTINGS.get("server_running"):
                data_module.APP_SETTINGS["server_running"] = ok
        except Exception:
            pass

    def _try_auto_login(self):
        try:
            from utils import firebase_client as fb
            if not fb.is_configured():
                return None
            user_data = fb.load_session()
            if user_data and user_data.get("id"):
                email = user_data.get("email", "")
                if email:
                    key = fb.encode_email(email)
                    profile = fb.db_get(f"users/{key}")
                    if profile:
                        return profile
                return user_data
        except Exception:
            pass
        return None

    # ── Navigation callbacks ──────────────────────────────────────────────────

    def _on_login(self, user_dict):
        data_module.CURRENT_USER = user_dict
        try:
            from utils import firebase_client as fb
            if fb.is_configured() and fb._REFRESH_TOKEN:
                fb.save_session(user_dict)
        except Exception:
            pass
        try:
            from utils import api_client
            api_client.register_user(user_dict)
        except Exception:
            pass
        self._launch_main(user_dict)
        self.sm.current = "main"

    def _launch_main(self, user_dict):
        if self.sm.has_screen("main"):
            self.sm.remove_widget(self.sm.get_screen("main"))
        from kivy_views.main_screen import MainScreen
        main = MainScreen(name="main", current_user=user_dict)
        self.sm.add_widget(main)

    # ── On stop ───────────────────────────────────────────────────────────────

    def on_stop(self):
        try:
            from utils.data import save_users, save_posts, save_messages
            save_users()
            save_posts()
            save_messages()
        except Exception:
            pass


if __name__ == "__main__":
    UniShareApp().run()
