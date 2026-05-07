import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QMessageBox,
                             QFileDialog, QDialog, QLineEdit, QTextEdit,
                             QFrame, QComboBox, QListWidget, QListWidgetItem,
                             QButtonGroup, QRadioButton, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont

from views.helpers import make_circle_pixmap
import utils.data as data_module

PINK   = "#1565C0"
DARK   = "#212121"
GRAY   = "#757575"
LIGHT  = "#E3F2FD"
WHITE  = "#FFFFFF"
GREEN  = "#43A047"
BLUE   = "#1565C0"

# ── Translations ──────────────────────────────────────────────────────────────
LANGS = {
    "Français": {
        "edit": "✏️ Modifier le profil",
        "change_photo": "📷 Changer",
        "resources": "Ressources",
        "followers": "Abonnés",
        "following": "Abonnements",
        "badges": "🏆 Mes Badges",
        "posts": "📱 Mes Publications",
        "see_later": "⏰ Voir Plus Tard",
        "no_posts": "Aucune publication pour le moment",
        "logout": "🚪 Se déconnecter",
        "lang": "🌐 Langue",
        "chat": "💬 Discuter",
        "delete": "🗑️ Retirer",
        "no_later": "Aucun profil sauvegardé",
        "followers_title": "👥 Abonnés",
        "following_title": "📌 Abonnements",
    },
    "English": {
        "edit": "✏️ Edit Profile",
        "change_photo": "📷 Change",
        "resources": "Resources",
        "followers": "Followers",
        "following": "Following",
        "badges": "🏆 My Badges",
        "posts": "📱 My Posts",
        "see_later": "⏰ See Later",
        "no_posts": "No posts yet",
        "logout": "🚪 Log Out",
        "lang": "🌐 Language",
        "chat": "💬 Chat",
        "delete": "🗑️ Remove",
        "no_later": "No saved profiles",
        "followers_title": "👥 Followers",
        "following_title": "📌 Following",
    },
    "العربية": {
        "edit": "✏️ تعديل الملف الشخصي",
        "change_photo": "📷 تغيير",
        "resources": "الموارد",
        "followers": "المتابعون",
        "following": "المتابَعون",
        "badges": "🏆 شاراتي",
        "posts": "📱 منشوراتي",
        "see_later": "⏰ المشاهدة لاحقاً",
        "no_posts": "لا توجد منشورات بعد",
        "logout": "🚪 تسجيل الخروج",
        "lang": "🌐 اللغة",
        "chat": "💬 محادثة",
        "delete": "🗑️ إزالة",
        "no_later": "لا يوجد ملفات محفوظة",
        "followers_title": "👥 المتابعون",
        "following_title": "📌 المتابَعون",
    },
}

def T(key):
    lang = data_module.APP_SETTINGS.get("language", "Français")
    return LANGS.get(lang, LANGS["Français"]).get(key, key)


# ─── Edit Profile Dialog ──────────────────────────────────────────────────────
class EditProfileDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Modifier le profil")
        self.setGeometry(60, 100, 360, 380)
        self.setStyleSheet("background:white;")
        vb = QVBoxLayout(self)
        vb.setContentsMargins(22, 20, 22, 20)
        vb.setSpacing(12)

        vb.addWidget(self._lbl("✏️ Modifier mon profil",
                               f"font-size:17px;font-weight:bold;color:{DARK};"))

        self.name_inp = QLineEdit(user.get("name", ""))
        self.name_inp.setStyleSheet(self._fs())
        vb.addWidget(self.name_inp)

        self.bio_inp = QTextEdit()
        self.bio_inp.setPlainText(user.get("bio", ""))
        self.bio_inp.setFixedHeight(90)
        self.bio_inp.setStyleSheet(self._fs())
        vb.addWidget(self.bio_inp)

        btns = QHBoxLayout()
        cancel = QPushButton("Annuler")
        cancel.setStyleSheet(f"background:{LIGHT};border-radius:18px;padding:10px 20px;")
        cancel.clicked.connect(self.reject)
        save = QPushButton("💾 Enregistrer")
        save.setStyleSheet(f"background:{PINK};color:white;border-radius:18px;"
                            "padding:10px 20px;font-weight:bold;border:none;")
        save.clicked.connect(self.accept)
        btns.addWidget(cancel)
        btns.addWidget(save)
        vb.addLayout(btns)

    @staticmethod
    def _fs():
        return ("border:1px solid #E0E0E0;border-radius:10px;"
                "padding:10px;font-size:13px;background:#FAFAFA;")

    @staticmethod
    def _lbl(text, style=""):
        l = QLabel(text)
        if style:
            l.setStyleSheet(style)
        return l

    def get_data(self):
        return {
            "name": self.name_inp.text().strip(),
            "bio": self.bio_inp.toPlainText().strip(),
        }


# ─── Followers / Following Dialog ────────────────────────────────────────────
class FollowersDialog(QDialog):
    def __init__(self, title, users, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(60, 100, 340, 460)
        self.setStyleSheet("background:white;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel(title)
        hdr.setStyleSheet(f"font-size:17px;font-weight:bold;color:{DARK};"
                           "padding:14px 16px; border-bottom:1px solid #E0E0E0;")
        layout.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        content = QWidget()
        vb = QVBoxLayout(content)
        vb.setContentsMargins(0, 8, 0, 8)
        vb.setSpacing(2)

        for user in users:
            row = QFrame()
            row.setStyleSheet("border-bottom:1px solid #F5F5F5;")
            row.setFixedHeight(64)
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(14, 8, 14, 8)
            r_layout.setSpacing(12)

            pix = make_circle_pixmap(
                user.get("avatar", "👤"),
                user.get("avatar_color", "#3498db"),
                44,
                user.get("photo_path")
            )
            av = QLabel()
            av.setPixmap(pix)
            av.setFixedSize(44, 44)
            r_layout.addWidget(av)

            info = QVBoxLayout()
            info.setSpacing(2)
            info.addWidget(QLabel(user.get("name", "")))
            sub = QLabel(user.get("school", ""))
            sub.setStyleSheet(f"font-size:11px;color:{GRAY};")
            info.addWidget(sub)
            r_layout.addLayout(info)
            r_layout.addStretch()

            vb.addWidget(row)

        vb.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)


# ─── See Later Dialog ─────────────────────────────────────────────────────────
class SeeLaterDialog(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self.setWindowTitle(T("see_later"))
        self.setGeometry(40, 80, 360, 500)
        self.setStyleSheet("background:white;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel(T("see_later"))
        hdr.setStyleSheet(f"font-size:17px;font-weight:bold;color:{DARK};"
                           "padding:14px 16px; border-bottom:1px solid #E0E0E0;")
        layout.addWidget(hdr)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none;")
        self.content = QWidget()
        self.c_layout = QVBoxLayout(self.content)
        self.c_layout.setContentsMargins(0, 8, 0, 8)
        self.c_layout.setSpacing(4)
        self._refresh()
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll, stretch=1)

    def _refresh(self):
        while self.c_layout.count():
            item = self.c_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        later = getattr(data_module, "SAVED_FOR_LATER", [])
        if not later:
            empty = QLabel(T("no_later"))
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color:{GRAY};font-size:14px;padding:40px;")
            self.c_layout.addWidget(empty)
            return

        for user in later:
            row = QFrame()
            row.setStyleSheet("border-bottom:1px solid #F5F5F5; background:white;")
            row.setFixedHeight(74)
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(12, 8, 12, 8)
            r_layout.setSpacing(10)

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
            info.setSpacing(2)
            name_lbl = QLabel(f"{user.get('name', '')}, {user.get('age', '')}")
            name_lbl.setStyleSheet(f"font-size:14px;font-weight:bold;color:{DARK};")
            school_lbl = QLabel(user.get("school", ""))
            school_lbl.setStyleSheet(f"font-size:11px;color:{GRAY};")
            info.addWidget(name_lbl)
            info.addWidget(school_lbl)
            r_layout.addLayout(info)
            r_layout.addStretch()

            # Chat button
            chat_btn = QPushButton(T("chat"))
            chat_btn.setStyleSheet(f"background:{PINK};color:white;border-radius:14px;"
                                    "padding:6px 12px;font-size:12px;")
            _user = user
            chat_btn.clicked.connect(lambda _, u=_user: self._chat(u))
            r_layout.addWidget(chat_btn)

            # Delete button
            del_btn = QPushButton("✕")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("background:#FFEBEE;color:#D32F2F;border-radius:15px;"
                                   "border:none;font-weight:bold;")
            del_btn.clicked.connect(lambda _, u=_user: self._remove(u))
            r_layout.addWidget(del_btn)

            self.c_layout.addWidget(row)

    def _chat(self, user):
        self.accept()
        try:
            self.mw.chats_view.add_conversation(user)
            self.mw.chat_view.set_partner(user)
            self.mw.go_to_chats()
        except Exception:
            pass

    def _remove(self, user):
        if hasattr(data_module, "SAVED_FOR_LATER"):
            data_module.SAVED_FOR_LATER = [
                u for u in data_module.SAVED_FOR_LATER if u["id"] != user["id"]
            ]
        self._refresh()


# ─── Settings Dialog ──────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, profile_view, parent=None):
        super().__init__(parent)
        self.pv = profile_view
        self.setWindowTitle("Paramètres")
        self.setGeometry(30, 60, 400, 760)
        self.setStyleSheet("background:#F5F7FA;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet(f"background:{PINK};")
        hdr.setFixedHeight(56)
        hdr_row = QHBoxLayout(hdr)
        hdr_row.setContentsMargins(12, 0, 12, 0)
        back = QPushButton("←")
        back.setFixedSize(38, 38)
        back.setStyleSheet("background:transparent;color:white;font-size:20px;border:none;")
        back.clicked.connect(self.accept)
        hdr_row.addWidget(back)
        title = QLabel("⚙️  Paramètres")
        title.setStyleSheet("color:white;font-size:17px;font-weight:bold;background:transparent;")
        hdr_row.addWidget(title)
        hdr_row.addStretch()
        root.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;background:#F5F7FA;")
        content = QWidget()
        content.setStyleSheet("background:#F5F7FA;")
        vb = QVBoxLayout(content)
        vb.setContentsMargins(0, 12, 0, 24)
        vb.setSpacing(16)

        # ── Section MON COMPTE ─────────────────────────────────────────────────
        vb.addWidget(self._section_label("MON COMPTE"))
        account_card = self._card([
            ("✏️", "Modifier le profil",       "",              self._edit_profile),
            ("📷", "Changer la photo",          "",              self._change_photo),
            ("🔑", "Changer le mot de passe",   "",              self._change_password),
        ])
        vb.addWidget(account_card)

        # ── Section CONFIDENTIALITÉ ────────────────────────────────────────────
        vb.addWidget(self._section_label("CONFIDENTIALITÉ"))
        self._privacy_toggle = None
        privacy_card = self._card([
            ("🔒", "Compte privé",
             "Seuls vos abonnés voient vos publications",
             self._toggle_privacy),
            ("👁", "Qui peut me contacter",
             "Tout le monde",
             self._contact_policy),
        ], toggles={0: data_module.APP_SETTINGS.get("account_private", False)})
        vb.addWidget(privacy_card)

        # ── Section PRÉFÉRENCES ────────────────────────────────────────────────
        vb.addWidget(self._section_label("PRÉFÉRENCES"))
        lang = data_module.APP_SETTINGS.get("language", "Français")
        notif = data_module.APP_SETTINGS.get("notifications", True)
        pref_card = self._card([
            ("🌐", "Langue",         lang,   self._change_language),
            ("🔔", "Notifications",  "",     self._toggle_notif),
        ], toggles={1: notif})
        vb.addWidget(pref_card)

        # ── Section RÉSEAU ─────────────────────────────────────────────────────────
        vb.addWidget(self._section_label("RÉSEAU & CONNEXION"))
        from utils import firebase_client as fb
        if fb.is_configured():
            fb_status = "🟢 Firebase connecté (mondial)"
            net_card = self._card([
                ("🔥", "Mode", "Firebase (en ligne)",    self._show_server_info),
                ("🌍", "Statut", fb_status,               self._show_server_info),
                ("🔗", "Projet", fb.FIREBASE_CONFIG.get("projectId", "—"), self._show_server_info),
            ])
        else:
            ip = data_module.APP_SETTINGS.get('server_ip', '127.0.0.1')
            port = data_module.APP_SETTINGS.get('server_port', 8765)
            running = data_module.APP_SETTINGS.get('server_running', False)
            status = "🟢 Serveur LAN actif" if running else "🔴 Mode hors ligne"
            net_card = self._card([
                ("🌐", "Adresse du serveur",     f"{ip}:{port}", self._show_server_info),
                ("📡", "Statut",                 status,          self._show_server_info),
                ("🔗", "Connecter à un serveur", "Entrer une IP", self._connect_server),
            ])
        vb.addWidget(net_card)

        # ── Section AIDE ───────────────────────────────────────────────────────
        vb.addWidget(self._section_label("AIDE & À PROPOS"))
        help_card = self._card([
            ("ℹ️",  "À propos de UniShare",  "Version 1.0",  self._about),
            ("🛟",  "Centre d'aide",         "",              self._help),
            ("⭐",  "Noter l'application",   "",              self._rate),
        ])
        vb.addWidget(help_card)

        # ── Déconnexion ────────────────────────────────────────────────────────
        logout_btn = QPushButton("🚪  Se déconnecter")
        logout_btn.setFixedHeight(52)
        logout_btn.setStyleSheet("""
            QPushButton{background:white;color:#D32F2F;border-radius:14px;
                font-size:15px;font-weight:bold;margin:0 16px;border:1.5px solid #FFCDD2;}
            QPushButton:hover{background:#FFEBEE;}
        """)
        logout_btn.clicked.connect(self._logout)
        vb.addWidget(logout_btn)

        delete_btn = QPushButton("🗑️  Supprimer le compte")
        delete_btn.setFixedHeight(48)
        delete_btn.setStyleSheet("""
            QPushButton{background:transparent;color:#9E9E9E;border:none;
                font-size:13px;margin:0 16px;}
            QPushButton:hover{color:#D32F2F;}
        """)
        delete_btn.clicked.connect(self._delete_account)
        vb.addWidget(delete_btn)

        scroll.setWidget(content)
        root.addWidget(scroll)

    # ── Helpers UI ────────────────────────────────────────────────────────────

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#9E9E9E;font-size:11px;font-weight:bold;"
                           "padding:0 16px;letter-spacing:0.5px;")
        return lbl

    def _card(self, rows, toggles=None):
        card = QFrame()
        card.setStyleSheet("background:white;border-radius:14px;margin:0 12px;")
        vb = QVBoxLayout(card)
        vb.setContentsMargins(0, 0, 0, 0)
        vb.setSpacing(0)
        for i, (icon, title, subtitle, action) in enumerate(rows):
            row = QFrame()
            row.setStyleSheet("background:transparent;")
            row.setCursor(Qt.PointingHandCursor)
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(16, 14, 16, 14)
            r_layout.setSpacing(12)

            ico = QLabel(icon)
            ico.setFixedSize(32, 32)
            ico.setAlignment(Qt.AlignCenter)
            ico.setStyleSheet(f"background:{LIGHT};border-radius:8px;font-size:16px;")
            r_layout.addWidget(ico)

            txt_col = QVBoxLayout()
            txt_col.setSpacing(1)
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"font-size:14px;color:{DARK};font-weight:500;")
            txt_col.addWidget(title_lbl)
            if subtitle:
                sub_lbl = QLabel(subtitle)
                sub_lbl.setStyleSheet(f"font-size:11px;color:{GRAY};")
                txt_col.addWidget(sub_lbl)
            r_layout.addLayout(txt_col)
            r_layout.addStretch()

            if toggles and i in toggles:
                toggle = self._make_toggle(toggles[i])
                toggle.clicked.connect(action)
                r_layout.addWidget(toggle)
            else:
                arrow = QLabel("›")
                arrow.setStyleSheet(f"color:{GRAY};font-size:20px;")
                r_layout.addWidget(arrow)
                row.mousePressEvent = lambda e, a=action: a()

            if i < len(rows) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("color:#F0F0F0;margin:0 16px;")
                vb.addWidget(row)
                vb.addWidget(sep)
            else:
                vb.addWidget(row)
        return card

    @staticmethod
    def _make_toggle(checked):
        btn = QPushButton("●" if checked else "○")
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedSize(46, 26)
        color = PINK if checked else "#BDBDBD"
        btn.setStyleSheet(f"""
            QPushButton{{background:{color};border-radius:13px;
                color:white;font-size:14px;border:none;}}
            QPushButton:checked{{background:{PINK};}}
        """)

        def _update(c, b=btn):
            b.setText("●" if c else "○")
            b.setStyleSheet(f"""
                QPushButton{{background:{'#1565C0' if c else '#BDBDBD'};border-radius:13px;
                    color:white;font-size:14px;border:none;}}
            """)

        btn.toggled.connect(_update)
        return btn

    # ── Actions ───────────────────────────────────────────────────────────────

    def _edit_profile(self):
        user = self.pv.controller.get_current_user()
        dlg = EditProfileDialog(user, self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data["name"]:
                user["name"] = data["name"]
            user["bio"] = data["bio"]
            self.pv.controller.update_user(user)
            self.pv._build_ui()

    def _change_photo(self):
        self.accept()
        self.pv._change_photo()

    def _change_password(self):
        dlg = ChangePasswordDialog(self.pv.controller.get_current_user(), self)
        dlg.exec_()

    def _toggle_privacy(self):
        current = data_module.APP_SETTINGS.get("account_private", False)
        data_module.APP_SETTINGS["account_private"] = not current
        data_module.save_settings()

    def _contact_policy(self):
        QMessageBox.information(self, "Confidentialité",
            "Paramètre : Tout le monde peut vous contacter.\n"
            "(Fonctionnalité de restriction à venir)")

    def _change_language(self):
        dlg = LanguageDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.pv._build_ui()
            self.accept()
            # Rouvrir les paramètres avec la nouvelle langue
            new_dlg = SettingsDialog(self.pv, self.pv)
            new_dlg.exec_()

    def _toggle_notif(self):
        current = data_module.APP_SETTINGS.get("notifications", True)
        data_module.APP_SETTINGS["notifications"] = not current
        data_module.save_settings()

    def _about(self):
        QMessageBox.information(self, "À propos de UniShare",
            "UniShare – Plateforme Étudiante Marocaine\n\n"
            "Version 1.0\n"
            "Connectez les étudiants, partagez le savoir.\n\n"
            "© 2025 UniShare")

    def _help(self):
        QMessageBox.information(self, "Centre d'aide",
            "Pour toute question ou problème :\n\n"
            "📧 support@unishare.ma\n"
            "🌐 www.unishare.ma/aide")

    def _rate(self):
        QMessageBox.information(self, "Noter l'application",
            "Merci pour votre soutien ! ⭐\n"
            "Votre avis nous aide à améliorer UniShare.")

    def _show_server_info(self):
        from utils import firebase_client as fb
        if fb.is_configured():
            project = fb.FIREBASE_CONFIG.get("projectId", "—")
            QMessageBox.information(self, "Connexion Firebase",
                f"🔥 UniShare est connecté à Firebase\n\n"
                f"Projet : {project}\n"
                f"Mode : En ligne mondial 🌍\n\n"
                f"Vos données sont synchronisées\n"
                f"en temps réel avec tous les utilisateurs.")
        else:
            ip   = data_module.APP_SETTINGS.get('server_ip', '127.0.0.1')
            port = data_module.APP_SETTINGS.get('server_port', 8765)
            QMessageBox.information(self, "Info Serveur",
                f"📡 Serveur UniShare actif\n\n"
                f"Adresse IP : {ip}\n"
                f"Port : {port}\n\n"
                f"Partagez cette adresse avec vos amis\n"
                f"pour qu'ils puissent se connecter :\n\n"
                f"http://{ip}:{port}")

    def _connect_server(self):
        from PyQt5.QtWidgets import QInputDialog
        from utils import api_client
        current = api_client.get_server_url()
        url, ok = QInputDialog.getText(self, "Connecter au serveur",
            "Entrez l'adresse du serveur\n(ex: http://192.168.1.10:8765):",
            text=current)
        if ok and url.strip():
            api_client.set_server_url(url.strip())
            if api_client.ping():
                QMessageBox.information(self, "Succès", f"✅ Connecté à {url}")
            else:
                QMessageBox.warning(self, "Erreur",
                    f"❌ Impossible de joindre {url}\nVérifiez l'adresse et le réseau.")

    def _logout(self):
        reply = QMessageBox.question(self, "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.accept()
            try:
                from utils import firebase_client as fb
                fb.clear_session()
                fb.logout()
            except Exception:
                pass
            self.pv.controller.logout()
            from utils.data import save_users, save_posts
            save_users()
            save_posts()

    def _delete_account(self):
        reply = QMessageBox.warning(self, "Supprimer le compte",
            "⚠️ Cette action est irréversible.\n"
            "Voulez-vous vraiment supprimer votre compte ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            user = self.pv.controller.get_current_user()
            email = user.get("email", "")
            if email in data_module.REGISTERED_USERS:
                del data_module.REGISTERED_USERS[email]
                data_module.save_users()
            self.accept()
            self.pv.controller.logout()


# ─── Language Dialog ───────────────────────────────────────────────────────────
class LanguageDialog(QDialog):
    LANGS_LIST = [
        ("🇫🇷", "Français"),
        ("🇬🇧", "English"),
        ("🇲🇦", "العربية"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Langue")
        self.setFixedSize(340, 290)
        self.setStyleSheet("background:white;")
        self._build()

    def _build(self):
        vb = QVBoxLayout(self)
        vb.setContentsMargins(0, 0, 0, 0)
        vb.setSpacing(0)

        hdr = QLabel("🌐  Choisir la langue")
        hdr.setStyleSheet(f"font-size:16px;font-weight:bold;color:{DARK};"
                           "padding:18px 20px 14px;border-bottom:1px solid #F0F0F0;")
        vb.addWidget(hdr)

        current = data_module.APP_SETTINGS.get("language", "Français")
        self._group = QButtonGroup(self)

        for flag, lang in self.LANGS_LIST:
            row = QFrame()
            row.setStyleSheet("border-bottom:1px solid #F5F5F5;")
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(20, 14, 20, 14)

            radio = QRadioButton(f"{flag}  {lang}")
            radio.setStyleSheet(f"font-size:14px;color:{DARK};")
            radio.setChecked(lang == current)
            radio.setProperty("lang_value", lang)
            self._group.addButton(radio)
            r_layout.addWidget(radio)
            vb.addWidget(row)

        vb.addStretch()
        btns = QHBoxLayout()
        btns.setContentsMargins(16, 12, 16, 12)
        cancel = QPushButton("Annuler")
        cancel.setStyleSheet(f"background:#F5F5F5;border-radius:10px;padding:10px 20px;"
                              f"color:{DARK};border:none;")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Appliquer")
        ok.setStyleSheet(f"background:{PINK};color:white;border-radius:10px;"
                          "padding:10px 20px;font-weight:bold;border:none;")
        ok.clicked.connect(self._apply)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        vb.addLayout(btns)

    def _apply(self):
        for btn in self._group.buttons():
            if btn.isChecked():
                data_module.APP_SETTINGS["language"] = btn.property("lang_value")
                data_module.save_settings()
                break
        self.accept()


# ─── Change Password Dialog ────────────────────────────────────────────────────
class ChangePasswordDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Changer le mot de passe")
        self.setFixedSize(340, 280)
        self.setStyleSheet("background:white;")
        self._build()

    def _build(self):
        vb = QVBoxLayout(self)
        vb.setContentsMargins(24, 20, 24, 20)
        vb.setSpacing(12)

        vb.addWidget(self._lbl("🔑 Changer le mot de passe",
                                f"font-size:16px;font-weight:bold;color:{DARK};"))

        self.old_pw  = self._field("Mot de passe actuel")
        self.new_pw  = self._field("Nouveau mot de passe")
        self.new_pw2 = self._field("Confirmer le nouveau")
        for f in [self.old_pw, self.new_pw, self.new_pw2]:
            f.setEchoMode(QLineEdit.Password)
            vb.addWidget(f)

        btns = QHBoxLayout()
        cancel = QPushButton("Annuler")
        cancel.setStyleSheet(f"background:#F5F5F5;border-radius:12px;padding:10px;border:none;color:{DARK};")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Enregistrer")
        save.setStyleSheet(f"background:{PINK};color:white;border-radius:12px;"
                            "padding:10px;font-weight:bold;border:none;")
        save.clicked.connect(self._apply)
        btns.addWidget(cancel)
        btns.addWidget(save)
        vb.addLayout(btns)

    def _field(self, ph):
        f = QLineEdit()
        f.setPlaceholderText(ph)
        f.setFixedHeight(44)
        f.setStyleSheet(f"border:1px solid #E0E0E0;border-radius:10px;"
                         f"padding:0 12px;font-size:13px;color:{DARK};background:white;")
        return f

    @staticmethod
    def _lbl(text, style=""):
        l = QLabel(text)
        if style:
            l.setStyleSheet(style)
        return l

    def _apply(self):
        import hashlib
        old = self.old_pw.text()
        new = self.new_pw.text()
        new2 = self.new_pw2.text()

        email = self.user.get("email", "")
        stored = data_module.REGISTERED_USERS.get(email, {}).get("password_hash", "")
        old_hash = hashlib.sha256(old.encode()).hexdigest()

        if stored and old_hash != stored:
            QMessageBox.warning(self, "Erreur", "Mot de passe actuel incorrect.")
            return
        if len(new) < 6:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 6 caractères.")
            return
        if new != new2:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return

        new_hash = hashlib.sha256(new.encode()).hexdigest()
        if email in data_module.REGISTERED_USERS:
            data_module.REGISTERED_USERS[email]["password_hash"] = new_hash
            data_module.save_users()
        QMessageBox.information(self, "Succès", "✅ Mot de passe modifié avec succès !")
        self.accept()


# ─── Profile View ─────────────────────────────────────────────────────────────
class ProfileView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._main_window = None
        self.setStyleSheet(f"background:{LIGHT};")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._scroll = None
        self._build_ui()

    def set_main_window(self, mw):
        self._main_window = mw

    def _build_ui(self):
        if self._scroll:
            self._layout.removeWidget(self._scroll)
            self._scroll.deleteLater()

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("border:none; background:transparent;")

        content = QWidget()
        content.setStyleSheet(f"background:{LIGHT};")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(0, 0, 0, 24)
        vbox.setSpacing(10)
        vbox.setAlignment(Qt.AlignTop)

        user = self.controller.get_current_user()

        vbox.addWidget(self._make_header(user))
        vbox.addWidget(self._make_stats(user))

        if user.get("badges"):
            vbox.addWidget(self._make_badges(user))

        vbox.addWidget(self._make_see_later_btn())
        vbox.addWidget(self._make_posts(user))
        vbox.addWidget(self._make_settings_btn())

        self._scroll.setWidget(content)
        self._layout.addWidget(self._scroll)

    # ─── Header ───────────────────────────────────────────────────────────────

    def _make_header(self, user):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0D47A1, stop:0.5 #1565C0, stop:1 #1976D2);
                border-bottom-left-radius: 30px;
                border-bottom-right-radius: 30px;
            }}
        """)
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(20, 24, 20, 28)
        vbox.setSpacing(10)
        vbox.setAlignment(Qt.AlignHCenter)

        # Circular avatar
        size = 110
        pix = make_circle_pixmap(
            user.get("avatar", "👤"),
            user.get("avatar_color", "#3498db"),
            size,
            user.get("photo_path")
        )
        av_container = QWidget()
        av_container.setFixedSize(size + 10, size + 30)
        av_container.setStyleSheet("background:transparent;")
        a_layout = QVBoxLayout(av_container)
        a_layout.setContentsMargins(0, 0, 0, 0)
        a_layout.setSpacing(2)

        self._avatar_lbl = QLabel()
        self._avatar_lbl.setPixmap(pix)
        self._avatar_lbl.setFixedSize(size, size)
        self._avatar_lbl.setAlignment(Qt.AlignCenter)
        self._avatar_lbl.setCursor(Qt.PointingHandCursor)
        self._avatar_lbl.setToolTip("Voir la photo en plein écran")
        self._avatar_lbl.mousePressEvent = lambda e: self._view_photo_fullscreen()
        a_layout.addWidget(self._avatar_lbl, alignment=Qt.AlignCenter)

        cam_lbl = QLabel(T("change_photo"))
        cam_lbl.setStyleSheet("color:rgba(255,255,255,0.85);font-size:11px;background:transparent;"
                               "text-decoration:underline;")
        cam_lbl.setAlignment(Qt.AlignCenter)
        cam_lbl.setCursor(Qt.PointingHandCursor)
        cam_lbl.setToolTip("Changer la photo de profil")
        cam_lbl.mousePressEvent = lambda e: self._change_photo()
        a_layout.addWidget(cam_lbl, alignment=Qt.AlignCenter)

        vbox.addWidget(av_container, alignment=Qt.AlignCenter)

        name_lbl = QLabel(user.get("name", "Étudiant"))
        name_lbl.setStyleSheet("color:white;font-size:22px;font-weight:bold;background:transparent;")
        name_lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(name_lbl)

        school_lbl = QLabel(f"🏫 {user.get('school', '')}")
        school_lbl.setStyleSheet("color:rgba(255,255,255,0.85);font-size:13px;background:transparent;")
        school_lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(school_lbl)

        major_lbl = QLabel(f"📖 {user.get('major', '')}")
        major_lbl.setStyleSheet(
            "color:white;background:rgba(255,255,255,0.25);border-radius:14px;"
            "padding:5px 14px;font-size:12px;font-weight:bold;"
        )
        major_lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(major_lbl, alignment=Qt.AlignCenter)

        bio = user.get("bio", "")
        if bio:
            bio_lbl = QLabel(bio)
            bio_lbl.setWordWrap(True)
            bio_lbl.setAlignment(Qt.AlignCenter)
            bio_lbl.setStyleSheet("color:rgba(255,255,255,0.80);font-size:12px;background:transparent;")
            vbox.addWidget(bio_lbl)

        edit_btn = QPushButton(T("edit"))
        edit_btn.setStyleSheet("""
            QPushButton{background:rgba(255,255,255,0.20);color:white;
                border:1px solid rgba(255,255,255,0.50);border-radius:20px;
                padding:8px 24px;font-size:13px;font-weight:bold;}
            QPushButton:hover{background:rgba(255,255,255,0.35);}
        """)
        edit_btn.clicked.connect(self._edit_profile)
        vbox.addWidget(edit_btn, alignment=Qt.AlignCenter)
        return card

    # ─── Stats (cliquables) ───────────────────────────────────────────────────

    def _make_stats(self, user):
        card = QFrame()
        card.setStyleSheet(f"background:{WHITE};border-radius:16px;margin:0 12px;")
        row = QHBoxLayout(card)
        row.setContentsMargins(10, 16, 10, 16)
        row.setSpacing(0)

        defs = [
            (str(self.controller.get_shared_resources_count()), "📚", T("resources"), None),
            (str(self.controller.get_followers_count()),         "👥", T("followers"), self._show_followers),
            (str(self.controller.get_following_count()),         "📌", T("following"), self._show_following),
        ]
        for i, (value, icon, label, callback) in enumerate(defs):
            stat = QWidget()
            stat.setCursor(Qt.PointingHandCursor if callback else Qt.ArrowCursor)
            vb = QVBoxLayout(stat)
            vb.setSpacing(2)
            vb.setContentsMargins(0, 0, 0, 0)
            vb.setAlignment(Qt.AlignCenter)

            num = QLabel(value)
            num.setStyleSheet(f"font-size:20px;font-weight:bold;color:{DARK};")
            num.setAlignment(Qt.AlignCenter)
            vb.addWidget(num)

            lbl = QLabel(f"{icon} {label}")
            lbl.setStyleSheet(f"font-size:11px;color:{GRAY};")
            lbl.setAlignment(Qt.AlignCenter)
            vb.addWidget(lbl)

            if callback:
                _cb = callback
                stat.mousePressEvent = lambda e, cb=_cb: cb()

            row.addWidget(stat, stretch=1)
            if i < len(defs) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.VLine)
                sep.setStyleSheet("color:#E0E0E0;")
                row.addWidget(sep)
        return card

    # ─── Badges ───────────────────────────────────────────────────────────────

    def _make_badges(self, user):
        card = QFrame()
        card.setStyleSheet(f"background:{WHITE};border-radius:16px;margin:0 12px;")
        vb = QVBoxLayout(card)
        vb.setContentsMargins(16, 14, 16, 14)
        vb.setSpacing(10)
        title = QLabel(T("badges"))
        title.setStyleSheet(f"font-weight:bold;font-size:15px;color:{DARK};")
        vb.addWidget(title)
        badges_row = QHBoxLayout()
        badges_row.setSpacing(8)
        for badge in user.get("badges", []):
            bl = QLabel(badge)
            bl.setStyleSheet(f"background:{LIGHT};color:{DARK};padding:6px 14px;"
                              "border-radius:16px;font-size:12px;border:1px solid #E0E0E0;")
            badges_row.addWidget(bl)
        badges_row.addStretch()
        vb.addLayout(badges_row)
        return card

    # ─── See Later button ─────────────────────────────────────────────────────

    def _make_see_later_btn(self):
        count = len(getattr(data_module, "SAVED_FOR_LATER", []))
        btn = QPushButton(f"⏰ {T('see_later')}  ({count})")
        btn.setStyleSheet(f"""
            QPushButton{{background:white;border-radius:16px;margin:0 12px;
                padding:14px;font-size:14px;font-weight:bold;color:{DARK};
                border:1px solid #E0E0E0;text-align:left;}}
            QPushButton:hover{{background:#E3F2FD;border-color:{PINK};color:{PINK};}}
        """)
        btn.clicked.connect(self._open_see_later)
        return btn

    # ─── Posts ────────────────────────────────────────────────────────────────

    def _make_posts(self, user):
        card = QFrame()
        card.setStyleSheet(f"background:{WHITE};border-radius:16px;margin:0 12px;")
        vb = QVBoxLayout(card)
        vb.setContentsMargins(16, 14, 16, 14)
        vb.setSpacing(10)
        title = QLabel(T("posts"))
        title.setStyleSheet(f"font-weight:bold;font-size:15px;color:{DARK};")
        vb.addWidget(title)

        posts = user.get("posts", [])
        if not posts:
            empty = QLabel(T("no_posts"))
            empty.setStyleSheet(f"color:{GRAY};font-size:13px;padding:8px 0;")
            vb.addWidget(empty)
        else:
            for post in posts:
                pc = QFrame()
                pc.setStyleSheet(f"background:{LIGHT};border-radius:12px;"
                                  "border:1px solid #E0E0E0;")
                pl = QVBoxLayout(pc)
                pl.setContentsMargins(12, 10, 12, 10)
                pl.setSpacing(6)
                content_lbl = QLabel(post.get("content", ""))
                content_lbl.setWordWrap(True)
                content_lbl.setStyleSheet(f"font-size:13px;color:{DARK};")
                pl.addWidget(content_lbl)
                stats_lbl = QLabel(f"❤️ {post.get('likes', 0)}  💬 {post.get('comments', 0)}")
                stats_lbl.setStyleSheet(f"font-size:11px;color:{GRAY};")
                pl.addWidget(stats_lbl)
                vb.addWidget(pc)
        return card

    # ─── Settings button ──────────────────────────────────────────────────────

    def _make_settings_btn(self):
        btn = QPushButton("⚙️  Paramètres & Compte")
        btn.setFixedHeight(54)
        btn.setStyleSheet(f"""
            QPushButton{{background:white;border-radius:16px;margin:0 12px;
                padding:0 20px;font-size:15px;font-weight:bold;color:{DARK};
                border:1px solid #E0E0E0;text-align:left;}}
            QPushButton:hover{{background:{LIGHT};border-color:{PINK};color:{PINK};}}
        """)
        btn.clicked.connect(self._open_settings)
        return btn

    # ─── Actions ─────────────────────────────────────────────────────────────

    def _view_photo_fullscreen(self):
        from views.fullscreen_photo import FullscreenPhotoDialog
        user = self.controller.get_current_user()
        dlg = FullscreenPhotoDialog(user, self)
        dlg.exec_()

    def _change_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une photo de profil", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            user = self.controller.get_current_user()
            user["photo_path"] = path
            self.controller.update_user(user)
            size = 110
            pix = make_circle_pixmap(
                user.get("avatar", "👤"),
                user.get("avatar_color", "#3498db"),
                size, path
            )
            self._avatar_lbl.setPixmap(pix)

    def _open_settings(self):
        dlg = SettingsDialog(self, self)
        dlg.exec_()
        self._build_ui()

    def _edit_profile(self):
        user = self.controller.get_current_user()
        dlg = EditProfileDialog(user, self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data["name"]:
                user["name"] = data["name"]
            user["bio"] = data["bio"]
            self.controller.update_user(user)
            self._build_ui()

    def _show_followers(self):
        users = getattr(data_module, "FAKE_USERS", [])[:4]
        dlg = FollowersDialog(T("followers_title"), users, self)
        dlg.exec_()

    def _show_following(self):
        users = getattr(data_module, "FAKE_USERS", [])[2:]
        dlg = FollowersDialog(T("following_title"), users, self)
        dlg.exec_()

    def _open_see_later(self):
        dlg = SeeLaterDialog(self._main_window, self)
        dlg.exec_()
        self._build_ui()  # refresh count

    def refresh(self):
        self._build_ui()
