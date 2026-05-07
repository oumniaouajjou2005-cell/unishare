import hashlib, time, os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QFrame, QMessageBox,
                             QComboBox, QStackedWidget, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QPixmap

# ── Palette officielle UniShare ───────────────────────────────────────────────
DARK_BLU = "#0D47A1"   # Bleu foncé    – bannière haut
MID_BLU  = "#1565C0"   # Bleu moyen    – fond milieu
PINK     = "#1976D2"   # Bleu vif      – boutons / actif
ROSE     = "#90CAF9"   # Bleu clair    – accents / bordures
LIGHT    = "#E3F2FD"   # Bleu pâle     – fond formulaire
GOLD     = "#FFB300"
WHITE    = "#FFFFFF"
DARK     = "#212121"
RED      = "#E53935"
GREEN    = "#2E7D32"

SCHOOLS = [
    "ENCG Casablanca", "ENCG Agadir", "ENCG Fès", "ENCG Marrakech",
    "ISCAE Rabat", "ISCAE Casablanca", "HEM Casablanca", "Mundiapolis",
    "FSJES Casablanca", "FSJES Rabat", "FSJES Tanger", "FSJES Marrakech",
    "EMI Rabat", "ENSAM Casablanca", "INPT Rabat", "ENSET Mohammedia",
    "INSEA Rabat", "EST Casablanca", "EST Rabat", "ENSA Marrakech",
    "Université Hassan II", "Université Mohammed V", "Autre"
]
MAJORS = [
    "Finance", "Marketing", "GRH", "Audit & Contrôle", "Informatique de Gestion",
    "Génie Informatique", "Génie Civil", "Génie Électrique", "Statistiques",
    "Droit des Affaires", "Économie", "Management", "Autre"
]
AVATARS_F = ["👩‍💼", "👩‍🎓", "👩‍💻", "👩‍🔬", "👩‍🏫", "👩‍🎨"]
AVATARS_M = ["👨‍💼", "👨‍🎓", "👨‍💻", "👨‍🔬", "👨‍🏫", "👨‍🎨"]
COLORS    = ["#9C27B0", "#E91E63", "#009688", "#1565C0", "#F57C00", "#2E7D32",
             "#6A1B9A", "#AD1457", "#00695C", "#0D47A1", "#E65100", "#1B5E20"]


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


class LoginView(QWidget):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{WHITE};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Bannière supérieure ───────────────────────────────────────────────
        banner = QWidget()
        banner.setFixedHeight(210)
        banner.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {DARK_BLU}, stop:0.55 {MID_BLU}, stop:1 {PINK});
            }}
        """)
        bl = QVBoxLayout(banner)
        bl.setAlignment(Qt.AlignCenter)
        bl.setSpacing(6)
        bl.setContentsMargins(20, 18, 20, 18)

        # Logo image
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(94, 94)
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("background:transparent;")
        try:
            from utils.logo_generator import get_logo_pixmap, ensure_logo
            ensure_logo()
            logo_pix = get_logo_pixmap(90)
            if logo_pix and not logo_pix.isNull():
                logo_lbl.setPixmap(logo_pix)
            else:
                logo_lbl.setText("🎓")
                logo_lbl.setStyleSheet("font-size:56px; background:transparent;")
        except Exception:
            logo_lbl.setText("🎓")
            logo_lbl.setStyleSheet("font-size:56px; background:transparent;")
        bl.addWidget(logo_lbl, alignment=Qt.AlignCenter)

        title = QLabel("UniShare")
        title.setStyleSheet(
            f"color:{WHITE}; font-size:28px; font-weight:bold;"
            " font-family:'Segoe UI'; background:transparent; letter-spacing:1px;")
        title.setAlignment(Qt.AlignCenter)
        bl.addWidget(title)

        sub = QLabel("Le savoir partagé · La réussite assurée")
        sub.setStyleSheet(f"color:{GOLD}; font-size:11px; background:transparent;"
                           " letter-spacing:0.5px;")
        sub.setAlignment(Qt.AlignCenter)
        bl.addWidget(sub)

        root.addWidget(banner)

        # ── Zone de formulaire scrollable ─────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:transparent;")

        content = QWidget()
        content.setStyleSheet(f"background:{WHITE};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(22, 20, 22, 20)
        cl.setSpacing(12)

        # ── Carte blanche centrale ─────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border-radius: 20px;
                border: 1px solid #E8E8E8;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 20)
        card_layout.setSpacing(0)

        # Onglets Se connecter / S'inscrire
        tab_row = QHBoxLayout()
        tab_row.setSpacing(0)
        self.btn_tab_login  = QPushButton("Se connecter")
        self.btn_tab_signup = QPushButton("S'inscrire")
        for btn in [self.btn_tab_login, self.btn_tab_signup]:
            btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
        self.btn_tab_login.clicked.connect(lambda: self._switch_tab(0))
        self.btn_tab_signup.clicked.connect(lambda: self._switch_tab(1))
        tab_row.addWidget(self.btn_tab_login)
        tab_row.addWidget(self.btn_tab_signup)
        card_layout.addLayout(tab_row)

        # Séparateur sous les onglets
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#E0E0E0; margin:0;")
        card_layout.addWidget(sep)
        card_layout.addSpacing(12)

        # Contenu empilé
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        self.stack.addWidget(self._build_login_tab())
        self.stack.addWidget(self._build_signup_tab())
        card_layout.addWidget(self.stack)

        cl.addWidget(card)

        cl.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)

        self._switch_tab(0)

    # ── Changement d'onglet ───────────────────────────────────────────────────
    def _switch_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        active = f"""
            QPushButton {{
                background: transparent; color: {PINK};
                border: none; border-bottom: 3px solid {PINK};
                font-size: 14px; font-weight: bold; padding-bottom: 6px;
            }}
        """
        inactive = f"""
            QPushButton {{
                background: transparent; color: #90A4AE;
                border: none; border-bottom: 2px solid #E0E0E0;
                font-size: 14px; font-weight: bold; padding-bottom: 6px;
            }}
        """
        self.btn_tab_login.setStyleSheet(active  if idx == 0 else inactive)
        self.btn_tab_signup.setStyleSheet(active if idx == 1 else inactive)

    # ── Composants réutilisables ──────────────────────────────────────────────
    def _field(self, placeholder, password=False):
        f = QLineEdit()
        f.setPlaceholderText(placeholder)
        if password:
            f.setEchoMode(QLineEdit.Password)
        f.setFixedHeight(46)
        f.setStyleSheet(f"""
            QLineEdit {{
                background: {WHITE};
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                padding: 0 14px; font-size: 14px; color: {DARK};
            }}
            QLineEdit:focus {{
                border: 2px solid {PINK};
                background: {WHITE};
            }}
        """)
        return f

    def _combo(self, items):
        c = QComboBox()
        c.addItems(items)
        c.setFixedHeight(46)
        c.setStyleSheet(f"""
            QComboBox {{
                background: {WHITE}; border: 1px solid #E0E0E0;
                border-radius: 12px; padding: 0 14px;
                font-size: 13px; color: {DARK};
            }}
            QComboBox:focus {{ border: 2px solid {PINK}; background: {WHITE}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
        """)
        return c

    def _primary_btn(self, text, color=None):
        color = color or PINK
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        darker = QColor(color).darker(120).name()
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 25px;
                font-size: 15px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        return btn

    # ── Onglet Connexion ──────────────────────────────────────────────────────
    def _build_login_tab(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 8, 0, 0)
        l.setSpacing(12)

        self.login_email = self._field("✉  Email étudiant")
        self.login_pw    = self._field("🔒  Mot de passe", password=True)
        l.addWidget(self.login_email)
        l.addWidget(self.login_pw)

        btn = self._primary_btn("Se connecter  →")
        btn.clicked.connect(self._do_login)
        l.addWidget(btn)
        return w

    def _do_login(self):
        email = self.login_email.text().strip().lower()
        pw    = self.login_pw.text()
        if not email or not pw:
            self._err("Remplis tous les champs.")
            return

        from utils import firebase_client as fb
        if fb.is_configured():
            result = fb.sign_in(email, pw)
            if result:
                key  = fb.encode_email(email)
                user = fb.db_get(f"users/{key}") or {}
                if not user:
                    user = {"id": result.get("localId", ""), "email": email,
                            "name": email, "avatar": "🎓", "avatar_color": "#1565C0",
                            "school": "", "major": "", "bio": "", "posts": [],
                            "badges": ["🎓 Nouveau"]}
                user["email_verified"] = fb.is_email_verified()
                self.login_success.emit(user)
            else:
                self._err("Email ou mot de passe incorrect.")
            return

        from utils.data import REGISTERED_USERS
        if email not in REGISTERED_USERS:
            self._err("Compte introuvable. Inscris-toi d'abord.")
            return
        if REGISTERED_USERS[email]["password_hash"] != hash_pw(pw):
            self._err("Mot de passe incorrect.")
            return
        user = {k: v for k, v in REGISTERED_USERS[email].items() if k != "password_hash"}
        self.login_success.emit(user)

    # ── Onglet Inscription ────────────────────────────────────────────────────
    def _build_signup_tab(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 8, 0, 0)
        l.setSpacing(10)

        self.su_fname  = self._field("👤  Prénom")
        self.su_lname  = self._field("👤  Nom")
        self.su_email  = self._field("✉  Email étudiant (@ac.ma, @edu.ma…)")
        self.su_pw     = self._field("🔒  Mot de passe (min. 6 car.)", password=True)
        self.su_pw2    = self._field("🔒  Confirmer le mot de passe", password=True)
        self.su_school = self._combo(["🏫 École / Université"] + SCHOOLS)
        self.su_major  = self._combo(["📖 Filière"] + MAJORS)

        for widget in [self.su_fname, self.su_lname, self.su_email,
                       self.su_pw, self.su_pw2, self.su_school, self.su_major]:
            l.addWidget(widget)

        terms = QLabel("En vous inscrivant, vous acceptez que votre email\nsoit un email étudiant valide.")
        terms.setStyleSheet(f"color:{ROSE}; font-size:11px;")
        terms.setAlignment(Qt.AlignCenter)
        l.addWidget(terms)

        btn = self._primary_btn("Créer mon compte  ✓", GREEN)
        btn.clicked.connect(self._do_signup)
        l.addWidget(btn)
        return w

    def _do_signup(self):
        fname  = self.su_fname.text().strip()
        lname  = self.su_lname.text().strip()
        email  = self.su_email.text().strip().lower()
        pw     = self.su_pw.text()
        pw2    = self.su_pw2.text()
        school = self.su_school.currentText()
        major  = self.su_major.currentText()

        if not all([fname, lname, email, pw, pw2]):
            self._err("Remplis tous les champs obligatoires.")
            return
        if school.startswith("🏫"):
            self._err("Sélectionne ton école.")
            return
        if major.startswith("📖"):
            self._err("Sélectionne ta filière.")
            return
        if pw != pw2:
            self._err("Les mots de passe ne correspondent pas.")
            return
        if len(pw) < 6:
            self._err("Mot de passe trop court (min. 6 caractères).")
            return

        import random
        avatar  = random.choice(AVATARS_F + AVATARS_M)
        color   = random.choice(COLORS)
        user_id = f"user_{int(time.time())}_{random.randint(1000,9999)}"

        new_user = {
            "id":            user_id,
            "name":          f"{fname} {lname}",
            "email":         email,
            "school":        school,
            "major":         major,
            "avatar":        avatar,
            "avatar_color":  color,
            "bio":           f"Étudiant(e) en {major} à {school}.",
            "posts":         [],
            "badges":        ["🎓 Nouveau"],
            "created_at":    time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        from utils import firebase_client as fb
        if fb.is_configured():
            result = fb.sign_up(email, pw)
            if not result:
                self._err("Erreur lors de la création du compte.\nCet email est peut-être déjà utilisé.")
                return
            new_user["id"] = result.get("localId", user_id)
            key = fb.encode_email(email)
            fb.db_set(f"users/{key}", new_user)
            fb.send_email_verification()
            QMessageBox.information(self, "Vérifie ton email 📧",
                f"Un email de confirmation a été envoyé à :\n{email}\n\n"
                "Clique sur le lien dans l'email pour activer ton compte,\n"
                "puis connecte-toi.")
            self._switch_tab(0)
            self.login_email.setText(email)
            return
        else:
            new_user["password_hash"] = hash_pw(pw)
            from utils.data import REGISTERED_USERS, save_users
            if email in REGISTERED_USERS:
                self._err("Cet email est déjà utilisé.")
                return
            REGISTERED_USERS[email] = new_user
            save_users()

        user = {k: v for k, v in new_user.items() if k != "password_hash"}
        QMessageBox.information(self, "Bienvenue !",
                                f"🎉 Compte créé !\nBienvenue sur UniShare, {fname} !")
        self.login_success.emit(user)

    def _err(self, msg):
        QMessageBox.warning(self, "Erreur", msg)
