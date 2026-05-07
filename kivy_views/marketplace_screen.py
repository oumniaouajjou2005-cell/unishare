import time as _time

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField

import utils.data as data_module

BLUE  = "#31487A"
DARK  = "#192338"
GRAY  = "#757575"
LIGHT = "#D9E1F1"
WHITE = "#FFFFFF"
GREEN = "#2E7D32"
GOLD  = "#F9A825"

CATEGORIES = ["Tous", "Finance", "Marketing", "GRH", "Informatique",
               "Droit", "Économie", "Langues", "Maths", "Sciences"]

FILE_TYPE_ICONS = {
    "PDF": "📕", "Word": "📘", "Excel": "📗",
    "Video": "🎬", "Autre": "📄",
}
FILE_TYPE_COLORS = {
    "PDF": "#E53935", "Word": "#1565C0", "Excel": "#2E7D32",
    "Video": "#6A1B9A", "Autre": "#546E7A",
}


def _hex(h):
    c = get_color_from_hex(h)
    return (c[0], c[1], c[2], 1)


# ── Product card ──────────────────────────────────────────────────────────────
class ProductCard(MDCard):
    def __init__(self, product, on_buy=None, on_rate=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(186), dp(220)),
            padding=dp(10),
            spacing=dp(6),
            elevation=2,
            ripple_behavior=True,
            **kwargs,
        )
        self.product = product
        self._build(on_buy, on_rate)

    def _build(self, on_buy, on_rate):
        ftype = self.product.get("file_type", "Autre")
        icon  = FILE_TYPE_ICONS.get(ftype, "📄")
        fcolor = FILE_TYPE_COLORS.get(ftype, "#546E7A")

        # File type badge + icon
        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(36),
            spacing=dp(6),
        )
        top_row.add_widget(MDLabel(
            text=icon, font_size=dp(26),
            size_hint=(None, None), size=(dp(34), dp(34)),
            halign="center",
        ))
        top_row.add_widget(MDLabel(
            text=ftype,
            theme_text_color="Custom",
            text_color=_hex(fcolor),
            font_style="Caption", bold=True,
        ))
        # Rating stars
        rating = self.product.get("rating", 0)
        stars = "★" * int(rating) + "☆" * (5 - int(rating))
        top_row.add_widget(MDLabel(
            text=stars,
            theme_text_color="Custom",
            text_color=_hex(GOLD),
            font_style="Caption",
        ))
        self.add_widget(top_row)

        # Title
        self.add_widget(MDLabel(
            text=self.product.get("title", "")[:32],
            theme_text_color="Custom",
            text_color=_hex(DARK),
            font_style="Subtitle2",
            bold=True,
            size_hint_y=None, height=dp(40),
            halign="left",
        ))

        # Category
        self.add_widget(MDLabel(
            text=self.product.get("category", ""),
            theme_text_color="Custom",
            text_color=_hex(GRAY),
            font_style="Caption",
            size_hint_y=None, height=dp(18),
        ))

        # Price + seller
        price_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(26),
        )
        price = self.product.get("price", 0)
        price_txt = "Gratuit" if not price else f"{price} MAD"
        price_row.add_widget(MDLabel(
            text=price_txt,
            theme_text_color="Custom",
            text_color=_hex(BLUE) if price else _hex(GREEN),
            font_style="Subtitle2", bold=True,
        ))
        price_row.add_widget(MDLabel(
            text=f"par {self.product.get('seller','')}",
            theme_text_color="Custom",
            text_color=_hex(GRAY),
            font_style="Caption",
            halign="right",
        ))
        self.add_widget(price_row)

        # Buy button
        btn_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(36),
            spacing=dp(6),
        )
        buy_btn = MDRaisedButton(
            text="📥 Obtenir",
            size_hint_x=1,
            height=dp(34),
            md_bg_color=_hex(BLUE),
            font_size=dp(12),
        )
        if on_buy:
            buy_btn.bind(on_release=lambda _, p=self.product: on_buy(p))
        btn_row.add_widget(buy_btn)

        rate_btn = MDIconButton(
            icon="star-outline",
            size_hint=(None, None),
            size=(dp(34), dp(34)),
            theme_icon_color="Custom",
            icon_color=_hex(GOLD),
        )
        if on_rate:
            rate_btn.bind(on_release=lambda _, p=self.product: on_rate(p))
        btn_row.add_widget(rate_btn)
        self.add_widget(btn_row)


# ── Add product dialog ────────────────────────────────────────────────────────
def _show_add_product_dialog(on_submit):
    content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))

    title_inp  = MDTextField(hint_text="Titre de la ressource", size_hint_y=None, height=dp(54))
    price_inp  = MDTextField(hint_text="Prix (0 = Gratuit)", size_hint_y=None, height=dp(54))
    desc_inp   = MDTextField(
        hint_text="Description…",
        multiline=True,
        size_hint_y=None, height=dp(90),
    )
    cat_spin   = Spinner(
        text="Catégorie",
        values=CATEGORIES[1:],
        size_hint_y=None, height=dp(46),
    )
    ftype_spin = Spinner(
        text="Type de fichier",
        values=list(FILE_TYPE_ICONS.keys()),
        size_hint_y=None, height=dp(46),
    )

    for w in [title_inp, price_inp, desc_inp, cat_spin, ftype_spin]:
        content.add_widget(w)

    btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
    cancel_btn = MDFlatButton(text="Annuler", size_hint_x=1)
    add_btn    = MDRaisedButton(
        text="Ajouter ✓", size_hint_x=1,
        md_bg_color=_hex(BLUE),
    )
    btn_row.add_widget(cancel_btn)
    btn_row.add_widget(add_btn)
    content.add_widget(btn_row)

    popup = Popup(title="Ajouter une ressource",
                  content=content,
                  size_hint=(0.92, None), height=dp(520))

    def _submit(_):
        title = title_inp.text.strip()
        if not title:
            return
        try:
            price = float(price_inp.text.strip() or "0")
        except ValueError:
            price = 0

        user = data_module.CURRENT_USER or {}
        product = {
            "id": str(int(_time.time())),
            "title": title,
            "description": desc_inp.text.strip(),
            "price": price,
            "category": cat_spin.text if cat_spin.text != "Catégorie" else "Autre",
            "file_type": ftype_spin.text if ftype_spin.text != "Type de fichier" else "Autre",
            "seller": user.get("name", "Moi"),
            "seller_id": user.get("id", ""),
            "rating": 0,
            "ratings_count": 0,
            "date": _time.strftime("%d/%m/%Y"),
        }
        popup.dismiss()
        on_submit(product)

    add_btn.bind(on_release=_submit)
    cancel_btn.bind(on_release=popup.dismiss)
    popup.open()


# ── Rating dialog ─────────────────────────────────────────────────────────────
def _show_rating_dialog(product, on_submit):
    content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
    content.add_widget(MDLabel(
        text=f"⭐ Noter « {product.get('title','')[:30]}… »",
        halign="center", size_hint_y=None, height=dp(36),
    ))

    stars_row = MDBoxLayout(
        orientation="horizontal",
        size_hint_y=None, height=dp(44),
        spacing=dp(6),
    )
    stars_row.spacing = dp(4)
    selected = [0]
    star_btns = []

    def _set_stars(val):
        selected[0] = val
        for i, b in enumerate(star_btns):
            b.text = "★" if i < val else "☆"
            b.text_color = _hex(GOLD) if i < val else _hex(GRAY)

    for i in range(1, 6):
        b = MDFlatButton(
            text="☆",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            theme_text_color="Custom",
            text_color=_hex(GRAY),
            font_size=dp(22),
        )
        b.bind(on_release=lambda _, v=i: _set_stars(v))
        star_btns.append(b)
        stars_row.add_widget(b)
    content.add_widget(stars_row)

    comment_inp = MDTextField(
        hint_text="Commentaire (optionnel)…",
        size_hint_y=None, height=dp(54),
    )
    content.add_widget(comment_inp)

    btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
    cancel = MDFlatButton(text="Annuler", size_hint_x=1)
    submit = MDRaisedButton(text="Envoyer ⭐", size_hint_x=1, md_bg_color=_hex(GOLD))
    btn_row.add_widget(cancel)
    btn_row.add_widget(submit)
    content.add_widget(btn_row)

    popup = Popup(title="Donner une note",
                  content=content,
                  size_hint=(0.85, None), height=dp(320))

    def _submit(_):
        if selected[0] == 0:
            return
        popup.dismiss()
        on_submit(product, selected[0], comment_inp.text.strip())

    submit.bind(on_release=_submit)
    cancel.bind(on_release=popup.dismiss)
    popup.open()


# ── Marketplace Screen ────────────────────────────────────────────────────────
class MarketplaceScreen(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self._current_category = "Tous"
        self._build_ui()
        self.load_products()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # ── Header ────────────────────────────────────────────────────────────
        hdr = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(54),
            padding=[dp(14), dp(8)],
            spacing=dp(8),
            md_bg_color=(1, 1, 1, 1),
        )
        hdr.add_widget(MDLabel(
            text="🛒 Marketplace",
            font_style="H6",
            theme_text_color="Custom",
            text_color=_hex(BLUE),
        ))
        hdr.add_widget(Widget())
        add_btn = MDRaisedButton(
            text="+ Ajouter",
            size_hint_x=None,
            md_bg_color=_hex(BLUE),
        )
        add_btn.bind(on_release=lambda _: self._show_add_dialog())
        hdr.add_widget(add_btn)
        root.add_widget(hdr)

        # ── Search bar ────────────────────────────────────────────────────────
        search_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(54),
            padding=[dp(12), dp(6)],
            spacing=dp(8),
            md_bg_color=(1, 1, 1, 1),
        )
        self.search_inp = MDTextField(
            hint_text="🔍 Rechercher…",
            size_hint_x=1,
        )
        self.search_inp.bind(text=lambda _, v: self._on_search(v))
        search_row.add_widget(self.search_inp)
        root.add_widget(search_row)

        # ── Category filter ───────────────────────────────────────────────────
        cat_scroll = ScrollView(
            size_hint=(1, None), height=dp(48),
            do_scroll_y=False, bar_width=0,
        )
        cat_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing=dp(8),
            padding=[dp(10), dp(6)],
        )
        cat_row.bind(minimum_width=cat_row.setter("width"))

        self._cat_btns = {}
        for cat in CATEGORIES:
            btn = MDRaisedButton(
                text=cat,
                size_hint=(None, None),
                height=dp(36),
                md_bg_color=_hex(BLUE) if cat == "Tous" else _hex(LIGHT),
                text_color=(1, 1, 1, 1) if cat == "Tous" else _hex(DARK),
                font_size=dp(12),
            )
            btn.bind(on_release=lambda _, c=cat: self._filter_category(c))
            cat_row.add_widget(btn)
            self._cat_btns[cat] = btn

        cat_scroll.add_widget(cat_row)
        root.add_widget(cat_scroll)

        # ── Products grid scroll ──────────────────────────────────────────────
        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(
            cols=2,
            size_hint_y=None,
            spacing=dp(10),
            padding=[dp(10), dp(10)],
        )
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def load_products(self):
        self.grid.clear_widgets()
        products = self.controller.get_products()
        query = self.search_inp.text.strip().lower() if hasattr(self, "search_inp") else ""

        shown = 0
        for prod in products:
            if self._current_category != "Tous":
                if prod.get("category", "") != self._current_category:
                    continue
            if query and query not in prod.get("title", "").lower():
                continue
            card = ProductCard(
                prod,
                on_buy=self._on_buy,
                on_rate=self._on_rate,
            )
            self.grid.add_widget(card)
            shown += 1

        if shown == 0:
            self.grid.add_widget(MDLabel(
                text="📭 Aucune ressource trouvée",
                halign="center",
                theme_text_color="Custom",
                text_color=_hex(GRAY),
                size_hint_y=None, height=dp(160),
            ))

    def _filter_category(self, cat):
        self._current_category = cat
        for c, btn in self._cat_btns.items():
            if c == cat:
                btn.md_bg_color = _hex(BLUE)
                btn.text_color  = (1, 1, 1, 1)
            else:
                btn.md_bg_color = _hex(LIGHT)
                btn.text_color  = _hex(DARK)
        self.load_products()

    def _on_search(self, query):
        self.load_products()

    def _show_add_dialog(self):
        def on_submit(product):
            self.controller.add_product(product)
            self.load_products()
        _show_add_product_dialog(on_submit)

    def _on_buy(self, product):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(MDLabel(
            text=f"📥 Obtenir : {product.get('title','')}",
            halign="center", font_style="H6",
            size_hint_y=None, height=dp(36),
        ))
        price = product.get("price", 0)
        content.add_widget(MDLabel(
            text="Ressource gratuite !" if not price else f"Prix : {price} MAD",
            halign="center",
            theme_text_color="Custom",
            text_color=_hex(GREEN) if not price else _hex(BLUE),
            size_hint_y=None, height=dp(30),
        ))

        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        ok_btn = MDRaisedButton(
            text="✓ Confirmer",
            size_hint_x=1,
            md_bg_color=_hex(GREEN),
        )
        cancel_btn = MDFlatButton(text="Annuler", size_hint_x=1)
        btn_row.add_widget(ok_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Obtenir une ressource",
                      content=content, size_hint=(0.85, None), height=dp(240))
        ok_btn.bind(on_release=popup.dismiss)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _on_rate(self, product):
        def on_submit(prod, stars, comment):
            old_count  = prod.get("ratings_count", 0)
            old_rating = prod.get("rating", 0)
            new_count  = old_count + 1
            new_rating = (old_rating * old_count + stars) / new_count
            prod["rating"] = round(new_rating, 1)
            prod["ratings_count"] = new_count
            self.controller.update_product(prod)
            self.load_products()
        _show_rating_dialog(product, on_submit)
