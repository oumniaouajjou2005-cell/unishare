import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QStackedWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import utils.data as data_module
from views.login_view import LoginView
from views.main_window import MainWindow


class AppRoot(QWidget):
    """Root widget : Login → MainWindow (avec auto-connexion si session sauvegardée)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("UniShare – Plateforme Étudiante Marocaine")
        self.setGeometry(100, 80, 430, 820)
        self.setMinimumSize(390, 700)

        # ── Charger la configuration Firebase ─────────────────────────────────
        try:
            from utils import firebase_client as fb
            fb.load_config()
            if fb.is_configured():
                data_module.APP_SETTINGS["firebase_enabled"] = True
                data_module.APP_SETTINGS["server_running"]   = True
            else:
                data_module.APP_SETTINGS["firebase_enabled"] = False
        except Exception:
            pass

        # ── Démarrer le serveur réseau LAN (fallback) ──────────────────────────
        try:
            from utils.network_server import start_server
            from utils import api_client
            ok, ip, port = start_server(8765)
            api_client.set_server_url(f"http://127.0.0.1:{port}")
            data_module.APP_SETTINGS["server_ip"]   = ip
            data_module.APP_SETTINGS["server_port"] = port
            if not data_module.APP_SETTINGS.get("server_running"):
                data_module.APP_SETTINGS["server_running"] = ok
        except Exception:
            pass

        # ── Interface ─────────────────────────────────────────────────────────
        self.stack = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        # ── Essayer l'auto-connexion ───────────────────────────────────────────
        saved_user = self._try_auto_login()
        if saved_user:
            # Session valide → aller directement à l'interface principale
            data_module.CURRENT_USER = saved_user
            # Placeholder de login (jamais affiché)
            self.login_view = LoginView()
            self.login_view.login_success.connect(self._on_login)
            self.stack.addWidget(self.login_view)
            self._launch_main(saved_user)
        else:
            # Pas de session → afficher l'écran de connexion
            self.login_view = LoginView()
            self.login_view.login_success.connect(self._on_login)
            self.stack.addWidget(self.login_view)
            self.stack.setCurrentIndex(0)

    def _try_auto_login(self):
        """Tente de restaurer la session précédente depuis le fichier local."""
        try:
            from utils import firebase_client as fb
            if not fb.is_configured():
                return None
            user_data = fb.load_session()
            if user_data and user_data.get("id"):
                # Rafraîchir le profil depuis Firebase
                email = user_data.get("email", "")
                if email:
                    key     = fb.encode_email(email)
                    profile = fb.db_get(f"users/{key}")
                    if profile:
                        return profile
                return user_data
        except Exception:
            pass
        return None

    def _on_login(self, user_dict):
        data_module.CURRENT_USER = user_dict
        # Sauvegarder la session pour auto-connexion future
        try:
            from utils import firebase_client as fb
            if fb.is_configured() and fb._REFRESH_TOKEN:
                fb.save_session(user_dict)
        except Exception:
            pass
        # Synchroniser le profil sur Firebase
        try:
            from utils import api_client
            api_client.register_user(user_dict)
        except Exception:
            pass
        self._launch_main(user_dict)

    def _launch_main(self, user_dict):
        if self.stack.count() > 1:
            old = self.stack.widget(1)
            self.stack.removeWidget(old)
            old.deleteLater()
        main_win = MainWindow(current_user=user_dict)
        self.stack.addWidget(main_win)
        self.stack.setCurrentIndex(1)
        self.setWindowTitle(f"UniShare – {user_dict['name']}")


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    def _on_quit():
        from utils.data import save_users, save_posts, save_messages
        save_users()
        save_posts()
        save_messages()

    app.aboutToQuit.connect(_on_quit)

    root = AppRoot()
    root.show()
    sys.exit(app.exec_())
