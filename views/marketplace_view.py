import os
import time as _time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton,
    QLineEdit, QComboBox, QDialog, QMessageBox, QFrame, QTextEdit,
    QFileDialog, QGridLayout, QSizePolicy, QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor

from views.helpers import make_circle_pixmap
import utils.data as data_module

# ── Palette officielle ────────────────────────────────────────────────────────
BLUE   = "#31487A"   # YinMn Blue   – boutons principaux
DARK   = "#192338"   # Oxford Blue  – textes sombres
GRAY   = "#757575"   # textes secondaires
LIGHT  = "#D9E1F1"   # Lavender     – fond clair
WHITE  = "#FFFFFF"
GREEN  = "#2E7D32"
GOLD   = "#F9A825"
JORDY  = "#8FB3E2"   # Jordy Blue   – bordures / accents

CATEGORIES = ["Tous", "Finance", "Marketing", "GRH", "Informatique",
               "Droit", "Économie", "Langues", "Maths", "Sciences"]

FILE_TYPE_ICONS = {
    "PDF": "📕", "Word": "📘", "Excel": "📗", "Video": "🎬", "Autre": "📄"
}
FILE_TYPE_COLORS = {
    "PDF": "#E53935", "Word": "#1565C0", "Excel": "#2E7D32",
    "Video": "#6A1B9A", "Autre": "#546E7A"
}


# ─── Star rating widget ───────────────────────────────────────────────────────
class StarRatingWidget(QWidget):
    rating_changed = pyqtSignal(int)

    def __init__(self, initial=0, max_stars=5, readonly=False, parent=None):
        super().__init__(parent)
        self._rating = initial
        self._stars = []
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(2)
        for i in range(1, max_stars + 1):
            btn = QPushButton("★")
            btn.setFixedSize(22, 22)
            filled = i <= initial
            btn.setStyleSheet(
                f"background:transparent;border:none;font-size:16px;"
                f"color:{'#F9A825' if filled else '#E0E0E0'};")
            if not readonly:
                _i = i
                btn.clicked.connect(lambda _, v=_i: self._set(v))
            self._stars.append(btn)
            row.addWidget(btn)
        row.addStretch()

    def _set(self, value):
        self._rating = value
        for i, btn in enumerate(self._stars):
            btn.setStyleSheet(
                f"background:transparent;border:none;font-size:16px;"
                f"color:{'#F9A825' if i < value else '#E0E0E0'};")
        self.rating_changed.emit(value)

    def value(self):
        return self._rating


# ─── Rating dialog ────────────────────────────────────────────────────────────
class RatingDialog(QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"Noter · {product['title']}")
        self.setStyleSheet("background:white;")
        self.setFixedSize(340, 220)
        vb = QVBoxLayout(self)
        vb.setContentsMargins(24, 24, 24, 24)
        vb.setSpacing(14)
        vb.addWidget(QLabel(f"⭐ Noter « {product['title'][:30]}… »"))
        self.stars = StarRatingWidget(0, 5)
        vb.addWidget(self.stars)
        self.comment = QLineEdit()
        self.comment.setPlaceholderText("Commentaire (optionnel)…")
        self.comment.setStyleSheet("border:1px solid #E0E0E0;border-radius:10px;padding:8px;")
        vb.addWidget(self.comment)
        btns = QHBoxLayout()
        cancel = QPushButton("Annuler")
        cancel.setStyleSheet(f"background:#F8FAFF;border-radius:16px;padding:9px 18px;")
        cancel.clicked.connect(self.reject)
        submit = QPushButton("Envoyer ⭐")
        submit.setStyleSheet(f"background:{GOLD};color:{DARK};border-radius:16px;"
                              "padding:9px 18px;font-weight:bold;")
        submit.clicked.connect(self.accept)
        btns.addWidget(cancel)
        btns.addWidget(submit)
        vb.addLayout(btns)

    def get_rating(self):
        return self.stars.value(), self.comment.text().strip()


# ─── Product detail dialog ────────────────────────────────────────────────────
class ProductDetailDialog(QDialog):
    def __init__(self, product, controller, main_window, parent=None):
        super().__init__(parent)
        self.product = product
        self.controller = controller
        self.main_window = main_window
        self.setWindowTitle(product["title"])
        self.setStyleSheet("background:white;")
        self.setGeometry(40, 80, 390, 580)
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setGeometry(0, 0, 390, 580)
        scroll.setStyleSheet("border:none;")
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Icône + type
        icon = FILE_TYPE_ICONS.get(self.product.get("file_type", ""), "📄")
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size:64px; background:#F8FAFF; border-radius:20px; padding:18px;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedHeight(120)
        layout.addWidget(icon_lbl)

        title = QLabel(self.product["title"])
        title.setStyleSheet(f"font-size:18px;font-weight:bold;color:{DARK};")
        title.setWordWrap(True)
        layout.addWidget(title)

        # Vendeur
        seller_row = QHBoxLayout()
        pix = make_circle_pixmap("👤", "#31487A", 36)
        sv = QLabel(); sv.setPixmap(pix); sv.setFixedSize(36, 36)
        seller_row.addWidget(sv)
        sl = QVBoxLayout()
        sn = QLabel(self.product.get("seller_name", ""))
        sn.setStyleSheet(f"font-size:13px;font-weight:bold;color:{DARK};")
        su = QLabel(self.product.get("university", ""))
        su.setStyleSheet(f"font-size:11px;color:{GRAY};")
        sl.addWidget(sn); sl.addWidget(su)
        seller_row.addLayout(sl); seller_row.addStretch()
        layout.addLayout(seller_row)

        # Étoiles + stats
        stars_row = QHBoxLayout()
        stars = StarRatingWidget(round(self.product.get("rating", 0)), 5, readonly=True)
        stars_row.addWidget(stars)
        rt = QLabel(f"⭐ {self.product.get('rating',0):.1f}  ·  "
                    f"{self.product.get('downloads',0)} téléchargements")
        rt.setStyleSheet(f"color:{GRAY};font-size:12px;")
        stars_row.addWidget(rt); stars_row.addStretch()
        layout.addLayout(stars_row)

        # Description
        desc = QLabel(self.product.get("description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size:13px;color:{DARK};")
        layout.addWidget(desc)

        # Tags
        tags_row = QHBoxLayout(); tags_row.setSpacing(8)
        for tag in [self.product.get("file_type",""), self.product.get("subject","")]:
            if tag:
                tc = FILE_TYPE_COLORS.get(tag, BLUE)
                tl = QLabel(tag)
                tl.setStyleSheet(f"background:{tc}22;color:{tc};border-radius:12px;"
                                  f"padding:4px 12px;font-size:11px;font-weight:bold;"
                                  f"border:1px solid {tc}44;")
                tags_row.addWidget(tl)
        tags_row.addStretch()
        layout.addLayout(tags_row)

        # Prix
        price_lbl = QLabel(f"🔥 {self.product.get('price', 0)} DH")
        price_lbl.setStyleSheet(f"font-size:26px;font-weight:bold;color:{GOLD};")
        layout.addWidget(price_lbl)

        # Bouton panier
        cart_btn = QPushButton("🛒  Ajouter au panier")
        cart_btn.setFixedHeight(50)
        cart_btn.setStyleSheet(f"""
            QPushButton{{background:{BLUE};color:white;border-radius:14px;
                font-size:15px;font-weight:bold;}}
            QPushButton:hover{{background:#1E2E4F;}}
        """)
        cart_btn.clicked.connect(self._add_to_cart)
        layout.addWidget(cart_btn)

        # Bouton noter
        rate_btn = QPushButton("⭐  Laisser une note")
        rate_btn.setFixedHeight(44)
        rate_btn.setStyleSheet(f"""
            QPushButton{{background:{GOLD};color:{DARK};border-radius:14px;
                font-size:14px;font-weight:bold;}}
            QPushButton:hover{{background:#F57F17;}}
        """)
        rate_btn.clicked.connect(self._rate_product)
        layout.addWidget(rate_btn)

        scroll.setWidget(content)

    def _add_to_cart(self):
        self.controller.add_to_cart(self.product)
        try:
            data_module.NOTIFICATIONS.append({
                "type": "market",
                "text": f"🛒 « {self.product['title']} » ajouté au panier.",
                "time": _time.strftime("%H:%M"), "read": False,
            })
        except Exception:
            pass
        QMessageBox.information(self, "Panier", f"✅ « {self.product['title']} » ajouté !")

    def _rate_product(self):
        dlg = RatingDialog(self.product, self)
        if dlg.exec_() == QDialog.Accepted:
            rating, _ = dlg.get_rating()
            if rating == 0:
                QMessageBox.warning(self, "Note", "Sélectionnez au moins 1 étoile.")
                return
            old = self.product.get("rating", 0)
            dl = max(1, self.product.get("downloads", 1))
            self.product["rating"] = round((old * dl + rating) / (dl + 1), 1)
            self.product["downloads"] = dl + 1
            QMessageBox.information(self, "Merci !", f"Note {rating}⭐ enregistrée !")


# ─── Carte produit (liste verticale) ─────────────────────────────────────────
class ProductCard(QFrame):
    def __init__(self, product, controller, main_window, parent=None):
        super().__init__(parent)
        self.product = product
        self.controller = controller
        self.main_window = main_window
        self.setStyleSheet(f"""
            QFrame{{
                background:{WHITE};
                border-radius:16px;
                border:1px solid {JORDY};
            }}
            QFrame:hover{{ border:1.5px solid {BLUE}; }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # ── Ligne titre + icône ───────────────────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        icon_txt = FILE_TYPE_ICONS.get(self.product.get("file_type", ""), "📄")
        icon_color = FILE_TYPE_COLORS.get(self.product.get("file_type", ""), BLUE)
        icon_lbl = QLabel(icon_txt)
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size:24px; background:{icon_color}18;"
                                f"border-radius:10px; border:1px solid {icon_color}33;")
        top_row.addWidget(icon_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel(self.product["title"])
        title_lbl.setStyleSheet(f"font-size:14px;font-weight:bold;color:{DARK};")
        title_lbl.setWordWrap(True)
        title_col.addWidget(title_lbl)

        seller = self.product.get("seller_name", "")
        univ   = self.product.get("university", "")
        seller_lbl = QLabel(f"👤 {seller}  ·  🏫 {univ}" if univ else f"👤 {seller}")
        seller_lbl.setStyleSheet(f"font-size:11px;color:{GRAY};")
        title_col.addWidget(seller_lbl)
        top_row.addLayout(title_col)
        layout.addLayout(top_row)

        # ── Description ───────────────────────────────────────────────────────
        desc = self.product.get("description", "")
        if len(desc) > 90:
            desc = desc[:90] + "…"
        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"font-size:12px;color:{GRAY};")
        layout.addWidget(desc_lbl)

        # ── Tags ──────────────────────────────────────────────────────────────
        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)
        for tag in [self.product.get("file_type",""), self.product.get("subject","")]:
            if tag:
                tc = FILE_TYPE_COLORS.get(tag, BLUE)
                tl = QLabel(f"  {tag}  ")
                tl.setStyleSheet(f"background:{tc}18;color:{tc};"
                                  f"border-radius:10px;font-size:11px;font-weight:bold;"
                                  f"border:1px solid {tc}44;padding:2px 0;")
                tags_row.addWidget(tl)
        tags_row.addStretch()
        layout.addLayout(tags_row)

        # ── Prix + étoiles ────────────────────────────────────────────────────
        info_row = QHBoxLayout()
        price_lbl = QLabel(f"🔥  {self.product.get('price', 0)} DH")
        price_lbl.setStyleSheet(f"font-size:18px;font-weight:bold;color:{GOLD};")
        info_row.addWidget(price_lbl)
        info_row.addStretch()

        rating = self.product.get("rating", 0)
        dl     = self.product.get("downloads", 0)
        stars_txt = "★" * round(rating) + "☆" * (5 - round(rating))
        stars_lbl = QLabel(f"<font color='#F9A825'>{stars_txt}</font>"
                            f"<font color='{GRAY}'> {rating:.1f}  ·  {dl} téléch.</font>")
        stars_lbl.setStyleSheet("font-size:12px;")
        info_row.addWidget(stars_lbl)
        layout.addLayout(info_row)

        # ── Bouton Ajouter au panier (pleine largeur) ─────────────────────────
        cart_btn = QPushButton("🛒  Ajouter au panier")
        cart_btn.setFixedHeight(44)
        cart_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cart_btn.setStyleSheet(f"""
            QPushButton{{background:{BLUE};color:white;border-radius:12px;
                font-size:13px;font-weight:bold;border:none;}}
            QPushButton:hover{{background:#1E2E4F;}}
        """)
        cart_btn.clicked.connect(self._add_to_cart)
        layout.addWidget(cart_btn)

        # Clic sur la carte → détail
        self.mousePressEvent = lambda e: self._open_detail()

    def _open_detail(self):
        dlg = ProductDetailDialog(self.product, self.controller, self.main_window, self)
        dlg.exec_()

    def _add_to_cart(self):
        self.controller.add_to_cart(self.product)
        try:
            data_module.NOTIFICATIONS.append({
                "type": "market",
                "text": f"🛒 « {self.product['title']} » ajouté au panier.",
                "time": _time.strftime("%H:%M"), "read": False,
            })
        except Exception:
            pass
        QMessageBox.information(self, "Panier", f"✅ « {self.product['title']} » ajouté au panier !")


# ─── Sell dialog ──────────────────────────────────────────────────────────────
class SellProductDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_file = None
        self.setWindowTitle("Mettre en vente")
        self.setStyleSheet("background:white;")
        self.setGeometry(40, 80, 390, 560)
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setGeometry(0, 0, 390, 560)
        scroll.setStyleSheet("border:none;")
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        hdr = QLabel("📤 Mettre en vente")
        hdr.setStyleSheet(f"font-size:18px;font-weight:bold;color:{DARK};")
        layout.addWidget(hdr)

        def field(ph):
            f = QLineEdit(); f.setPlaceholderText(ph)
            f.setFixedHeight(46)
            f.setStyleSheet(f"border:1.5px solid {JORDY};border-radius:12px;"
                             f"padding:0 14px;font-size:13px;background:{LIGHT}55;")
            return f

        self.title_inp = field("Titre du produit *")
        layout.addWidget(self.title_inp)

        self.desc_inp = QTextEdit()
        self.desc_inp.setPlaceholderText("Description…")
        self.desc_inp.setFixedHeight(80)
        self.desc_inp.setStyleSheet(f"border:1.5px solid {JORDY};border-radius:12px;"
                                     f"padding:10px;font-size:13px;background:{LIGHT}55;")
        layout.addWidget(self.desc_inp)

        self.price_inp = field("Prix (DH) *")
        layout.addWidget(self.price_inp)

        def combo(items):
            c = QComboBox(); c.addItems(items)
            c.setFixedHeight(46)
            c.setStyleSheet(f"padding:0 14px;border-radius:12px;border:1.5px solid {JORDY};"
                             f"font-size:13px;background:{LIGHT}55;")
            return c

        self.type_combo = combo(["PDF", "Word", "Excel", "Video", "Autre"])
        layout.addWidget(self.type_combo)
        self.subj_combo = combo(CATEGORIES[1:])
        layout.addWidget(self.subj_combo)

        f_row = QHBoxLayout()
        pick_btn = QPushButton("📂 Choisir un fichier")
        pick_btn.setFixedHeight(44)
        pick_btn.setStyleSheet(f"background:{BLUE};color:white;border-radius:12px;"
                                "padding:0 16px;font-size:13px;font-weight:bold;border:none;")
        pick_btn.clicked.connect(self._pick_file)
        self.file_lbl = QLabel("Aucun fichier sélectionné")
        self.file_lbl.setStyleSheet(f"color:{GRAY};font-size:12px;")
        f_row.addWidget(pick_btn)
        f_row.addWidget(self.file_lbl, stretch=1)
        layout.addLayout(f_row)

        btns = QHBoxLayout()
        cancel = QPushButton("Annuler")
        cancel.setFixedHeight(46)
        cancel.setStyleSheet(f"background:#F8FAFF;border-radius:14px;padding:0 20px;"
                              "font-size:13px;border:none;")
        cancel.clicked.connect(self.reject)
        submit = QPushButton("💰 Mettre en vente")
        submit.setFixedHeight(46)
        submit.setStyleSheet(f"background:{GREEN};color:white;border-radius:14px;"
                              "padding:0 20px;font-size:13px;font-weight:bold;border:none;")
        submit.clicked.connect(self._submit)
        btns.addWidget(cancel)
        btns.addWidget(submit)
        layout.addLayout(btns)
        scroll.setWidget(content)

    def _pick_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier", "", "Tous (*)")
        if path:
            self.selected_file = path
            self.file_lbl.setText(f"✅ {os.path.basename(path)}")
            self.file_lbl.setStyleSheet(f"color:{GREEN};font-size:12px;")

    def _submit(self):
        title = self.title_inp.text().strip()
        price_txt = self.price_inp.text().strip()
        if not title or not price_txt:
            QMessageBox.warning(self, "Erreur", "Titre et prix obligatoires.")
            return
        try:
            price = int(price_txt)
            if price <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Prix invalide.")
            return
        user = data_module.CURRENT_USER or {}
        product = {
            "id": str(int(_time.time())),
            "title": title,
            "description": self.desc_inp.toPlainText().strip(),
            "price": price,
            "seller_id": user.get("id", "current_user"),
            "seller_name": user.get("name", "Moi"),
            "file_type": self.type_combo.currentText(),
            "subject": self.subj_combo.currentText(),
            "university": user.get("school", ""),
            "major": self.subj_combo.currentText(),
            "rating": 0, "downloads": 0,
            "file_path": self.selected_file,
        }
        self.controller.add_product(product)
        QMessageBox.information(self, "Succès", f"✅ « {title} » mis en vente !")
        self.accept()


# ─── Cart dialog ──────────────────────────────────────────────────────────────
class CartDialog(QDialog):
    def __init__(self, controller, main_window, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.main_window = main_window
        self.setWindowTitle("Mon Panier")
        self.setStyleSheet("background:white;")
        self.setGeometry(40, 80, 390, 500)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("🛒 Mon Panier")
        hdr.setStyleSheet(f"font-size:20px;font-weight:bold;color:{DARK};"
                           "padding:16px; border-bottom:1px solid #E0E0E0;")
        layout.addWidget(hdr)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none;")
        self.content = QWidget()
        self.c_layout = QVBoxLayout(self.content)
        self.c_layout.setAlignment(Qt.AlignTop)
        self.c_layout.setContentsMargins(12, 12, 12, 12)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll, stretch=1)

        self.total_lbl = QLabel("")
        self.total_lbl.setStyleSheet(f"font-size:18px;font-weight:bold;color:{DARK};"
                                      "padding:12px 16px; border-top:1px solid #E0E0E0;")
        self.total_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.total_lbl)

        btns = QHBoxLayout()
        btns.setContentsMargins(12, 8, 12, 12)
        clear_btn = QPushButton("🗑️ Vider")
        clear_btn.setFixedHeight(44)
        clear_btn.setStyleSheet("background:#FFEBEE;color:#D32F2F;border-radius:14px;"
                                 "padding:0 16px;font-weight:bold;border:none;")
        clear_btn.clicked.connect(self._clear)
        buy_btn = QPushButton("💬 Contacter le vendeur")
        buy_btn.setFixedHeight(44)
        buy_btn.setStyleSheet(f"background:{BLUE};color:white;border-radius:14px;"
                               "padding:0 16px;font-weight:bold;border:none;")
        buy_btn.clicked.connect(self._contact_seller)
        btns.addWidget(clear_btn)
        btns.addWidget(buy_btn)
        layout.addLayout(btns)
        self._refresh()

    def _refresh(self):
        while self.c_layout.count():
            item = self.c_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        cart = self.controller.get_cart()
        if not cart:
            empty = QLabel("🛍️ Votre panier est vide")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"padding:50px;color:{GRAY};font-size:16px;")
            self.c_layout.addWidget(empty)
        else:
            for product in cart:
                row = QFrame()
                row.setStyleSheet(f"background:#F8FAFF;border-radius:12px;margin-bottom:8px;")
                r_layout = QHBoxLayout(row)
                r_layout.setContentsMargins(12, 10, 12, 10)
                icon = FILE_TYPE_ICONS.get(product.get("file_type", ""), "📄")
                il = QLabel(icon); il.setStyleSheet("font-size:28px;")
                r_layout.addWidget(il)
                info = QVBoxLayout()
                info.addWidget(QLabel(product["title"]))
                info.addWidget(QLabel(f"💰 {product['price']} DH"))
                r_layout.addLayout(info); r_layout.addStretch()
                rm = QPushButton("✕")
                rm.setFixedSize(30, 30)
                rm.setStyleSheet("background:#FFEBEE;color:#D32F2F;border-radius:15px;"
                                  "border:none;font-weight:bold;")
                _p = product
                rm.clicked.connect(lambda _, p=_p: self._remove(p))
                r_layout.addWidget(rm)
                self.c_layout.addWidget(row)
        self.total_lbl.setText(f"Total : {self.controller.get_cart_total()} DH")

    def _remove(self, product):
        self.controller.remove_from_cart(product["id"])
        self._refresh()

    def _clear(self):
        reply = QMessageBox.question(self, "Vider", "Vider le panier ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.cart.clear()
            self._refresh()

    def _contact_seller(self):
        cart = self.controller.get_cart()
        if not cart:
            QMessageBox.warning(self, "Panier vide", "Votre panier est vide.")
            return
        first = cart[0]
        seller = {
            "id": first.get("seller_id", "seller_1"),
            "name": first.get("seller_name", "Vendeur"),
            "school": first.get("university", ""),
            "major": first.get("subject", ""),
            "avatar": "👤", "avatar_color": BLUE, "bio": "Vendeur UniShare",
        }
        items_txt = "\n".join([f"• {p['title']} ({p['price']} DH)" for p in cart])
        auto_msg = (f"Bonjour ! Je suis intéressé(e) par :\n{items_txt}\n"
                    f"Total : {self.controller.get_cart_total()} DH\n"
                    "Est-ce toujours disponible ? 😊")
        try:
            if hasattr(self.main_window, "chats_view"):
                self.main_window.chats_view.add_conversation(seller)
            if hasattr(self.main_window, "chat_view"):
                self.main_window.chat_view.set_partner(seller)
                self.main_window.chat_view.messages.append({
                    "sender": "moi", "text": auto_msg,
                    "time": _time.strftime("%H:%M"),
                })
                self.main_window.chat_view._refresh_messages()
            self.accept()
            self.main_window.go_to_chats()
        except Exception:
            QMessageBox.information(self, "Message envoyé",
                                    f"Votre demande a été envoyée à {seller['name']} !\n\n{auto_msg}")


# ─── Marketplace View ─────────────────────────────────────────────────────────
class MarketplaceView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.my_controller = controller
        self.main_window = None
        self.all_products = []
        self.setStyleSheet(f"background:#F8FAFF;")
        self._build_ui()

    def set_main_window(self, mw):
        self.main_window = mw

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Onglets Boutique / Mes Ventes ─────────────────────────────────────
        tabs_bar = QWidget()
        tabs_bar.setStyleSheet(f"background:{WHITE}; border-bottom:1px solid {JORDY};")
        tabs_bar.setFixedHeight(46)
        tabs_row = QHBoxLayout(tabs_bar)
        tabs_row.setContentsMargins(0, 0, 0, 0)
        tabs_row.setSpacing(0)

        self.tab_boutique  = self._tab_btn("🛍  Boutique")
        self.tab_mesventes = self._tab_btn("📦  Mes Ventes")
        self.tab_boutique.clicked.connect(lambda: self._switch_tab(0))
        self.tab_mesventes.clicked.connect(lambda: self._switch_tab(1))
        tabs_row.addWidget(self.tab_boutique)
        tabs_row.addWidget(self.tab_mesventes)
        tabs_row.addStretch()

        # Bouton panier (à droite de la barre d'onglets)
        cart_btn = QPushButton("🛒")
        cart_btn.setFixedSize(46, 46)
        cart_btn.setStyleSheet(f"background:transparent;border:none;font-size:22px;")
        cart_btn.setCursor(Qt.PointingHandCursor)
        cart_btn.clicked.connect(self._show_cart)
        tabs_row.addWidget(cart_btn)

        layout.addWidget(tabs_bar)

        # ── Contenu empilé ─────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_boutique())
        self.stack.addWidget(self._build_mes_ventes())
        layout.addWidget(self.stack, stretch=1)

        self._switch_tab(0)
        self.load_products()

    def _tab_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(46)
        btn.setMinimumWidth(130)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setCheckable(True)
        return btn

    def _switch_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        active = (f"QPushButton{{background:transparent;color:{BLUE};"
                   f"border:none;border-bottom:3px solid {BLUE};"
                   f"font-size:13px;font-weight:bold;padding:0 20px;}}")
        inactive = (f"QPushButton{{background:transparent;color:{GRAY};"
                     "border:none;border-bottom:2px solid transparent;"
                     "font-size:13px;padding:0 20px;}}"
                     f"QPushButton:hover{{color:{BLUE};}}")
        self.tab_boutique.setStyleSheet(active if idx == 0 else inactive)
        self.tab_mesventes.setStyleSheet(active if idx == 1 else inactive)
        if idx == 1:
            self._refresh_mes_ventes()

    # ── Boutique ──────────────────────────────────────────────────────────────
    def _build_boutique(self):
        w = QWidget()
        w.setStyleSheet(f"background:#F8FAFF;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Bandeau Marketplace UniShare
        header_card = QFrame()
        header_card.setStyleSheet(f"""
            QFrame{{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0D47A1, stop:1 #1976D2);
                border-radius:0px;
            }}
        """)
        header_card.setFixedHeight(60)
        hc_row = QHBoxLayout(header_card)
        hc_row.setContentsMargins(16, 0, 16, 0)

        mkt_lbl = QLabel("🛒  Marketplace UniShare")
        mkt_lbl.setStyleSheet("color:white;font-size:18px;font-weight:bold;background:transparent;")
        hc_row.addWidget(mkt_lbl)
        hc_row.addStretch()

        sell_btn = QPushButton("➕ Vendre")
        sell_btn.setFixedHeight(34)
        sell_btn.setStyleSheet(f"background:{GOLD};color:{DARK};border-radius:12px;"
                                "padding:0 14px;font-size:12px;font-weight:bold;border:none;")
        sell_btn.clicked.connect(self._sell)
        hc_row.addWidget(sell_btn)

        layout.addWidget(header_card)

        # Barre de recherche
        search_bar = QFrame()
        search_bar.setStyleSheet(f"background:{WHITE};border-bottom:1px solid {JORDY};")
        s_row = QHBoxLayout(search_bar)
        s_row.setContentsMargins(12, 10, 12, 10)
        s_row.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Rechercher un cours, mémoire, fiche…")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(f"""
            QLineEdit{{background:{WHITE};border:1.5px solid {JORDY};
                border-radius:10px;padding:0 14px;font-size:13px;color:{DARK};}}
            QLineEdit:focus{{border:2px solid {BLUE};background:{WHITE};}}
        """)
        self.search_input.textChanged.connect(self._do_search)
        s_row.addWidget(self.search_input, stretch=1)

        rch_btn = QPushButton("Rechercher")
        rch_btn.setFixedHeight(40)
        rch_btn.setStyleSheet(f"background:{BLUE};color:white;border-radius:10px;"
                               "padding:0 14px;font-size:13px;font-weight:bold;border:none;")
        rch_btn.clicked.connect(self._do_search)
        s_row.addWidget(rch_btn)

        flt_btn = QPushButton("⚙ Filtrer")
        flt_btn.setFixedHeight(40)
        flt_btn.setStyleSheet(f"background:{GOLD};color:{DARK};border-radius:10px;"
                               "padding:0 14px;font-size:13px;font-weight:bold;border:none;")
        flt_btn.clicked.connect(self._show_filter)
        s_row.addWidget(flt_btn)

        layout.addWidget(search_bar)

        # Liste produits
        self.products_scroll = QScrollArea()
        self.products_scroll.setWidgetResizable(True)
        self.products_scroll.setStyleSheet(f"border:none;background:#F8FAFF;")
        self.products_content = QWidget()
        self.products_content.setStyleSheet(f"background:#F8FAFF;")
        self.products_layout = QVBoxLayout(self.products_content)
        self.products_layout.setContentsMargins(12, 12, 12, 12)
        self.products_layout.setSpacing(10)
        self.products_layout.setAlignment(Qt.AlignTop)
        self.products_scroll.setWidget(self.products_content)
        layout.addWidget(self.products_scroll, stretch=1)
        return w

    # ── Mes Ventes ────────────────────────────────────────────────────────────
    def _build_mes_ventes(self):
        w = QWidget()
        w.setStyleSheet(f"background:#F8FAFF;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        hdr = QFrame()
        hdr.setStyleSheet(f"background:{WHITE};border-bottom:1px solid {JORDY};")
        hdr.setFixedHeight(56)
        h_row = QHBoxLayout(hdr)
        h_row.setContentsMargins(16, 8, 16, 8)
        h_row.addWidget(QLabel("📦  Mes produits en vente"))
        h_row.addStretch()
        sell_btn2 = QPushButton("➕ Mettre en vente")
        sell_btn2.setFixedHeight(36)
        sell_btn2.setStyleSheet(f"background:{GREEN};color:white;border-radius:12px;"
                                 "padding:0 14px;font-size:13px;font-weight:bold;border:none;")
        sell_btn2.clicked.connect(self._sell)
        h_row.addWidget(sell_btn2)
        layout.addWidget(hdr)

        self.mv_scroll = QScrollArea()
        self.mv_scroll.setWidgetResizable(True)
        self.mv_scroll.setStyleSheet(f"border:none;background:#F8FAFF;")
        self.mv_content = QWidget()
        self.mv_content.setStyleSheet(f"background:#F8FAFF;")
        self.mv_layout = QVBoxLayout(self.mv_content)
        self.mv_layout.setContentsMargins(12, 12, 12, 12)
        self.mv_layout.setSpacing(10)
        self.mv_layout.setAlignment(Qt.AlignTop)
        self.mv_scroll.setWidget(self.mv_content)
        layout.addWidget(self.mv_scroll, stretch=1)
        return w

    def _refresh_mes_ventes(self):
        while self.mv_layout.count():
            item = self.mv_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        my_products = self.my_controller.get_my_products()
        if not my_products:
            empty = QLabel("📭 Vous n'avez pas encore mis de produits en vente.\n\n"
                           "Cliquez sur « Mettre en vente » pour commencer !")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color:{GRAY};font-size:14px;padding:60px;")
            self.mv_layout.addWidget(empty)
        else:
            for p in my_products:
                card = ProductCard(p, self.my_controller, self.main_window, self)
                self.mv_layout.addWidget(card)

    # ── Chargement + filtrage ─────────────────────────────────────────────────
    def load_products(self):
        self.all_products = self.my_controller.get_all_products()
        self._display_products(self.all_products)

    def _do_search(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self._display_products(self.all_products)
            return
        filtered = [p for p in self.all_products
                    if query in p.get("title", "").lower()
                    or query in p.get("description", "").lower()
                    or query in p.get("subject", "").lower()]
        self._display_products(filtered)

    def _show_filter(self):
        """Popup de filtre par catégorie."""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu{{background:white;border:1px solid {JORDY};border-radius:12px;padding:6px;}}
            QMenu::item{{padding:8px 20px;font-size:13px;color:{DARK};border-radius:8px;}}
            QMenu::item:selected{{background:#F8FAFF;color:{BLUE};}}
        """)
        for cat in CATEGORIES:
            act = menu.addAction(cat)
            _cat = cat
            act.triggered.connect(lambda _, c=_cat: self._filter_by_cat(c))
        menu.exec_(self.cursor().pos())

    def _filter_by_cat(self, cat):
        if cat == "Tous":
            self._display_products(self.all_products)
        else:
            filtered = [p for p in self.all_products
                        if p.get("subject") == cat or p.get("major") == cat]
            self._display_products(filtered)

    def _display_products(self, products):
        while self.products_layout.count():
            item = self.products_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not products:
            empty = QLabel("📭 Aucun produit trouvé")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"padding:60px;color:{GRAY};font-size:16px;")
            self.products_layout.addWidget(empty)
            return

        for product in products:
            card = ProductCard(product, self.my_controller, self.main_window, self)
            self.products_layout.addWidget(card)

    def _show_cart(self):
        dlg = CartDialog(self.my_controller, self.main_window, self)
        dlg.exec_()

    def _sell(self):
        dlg = SellProductDialog(self.my_controller, self)
        if dlg.exec_():
            self.load_products()
            self._push_notif("🛒 Votre produit a été mis en vente avec succès !")

    def _push_notif(self, message, kind="market"):
        try:
            if self.main_window and self.main_window._notif_manager:
                self.main_window._notif_manager.push(message, kind, "🛒")
        except Exception:
            pass
