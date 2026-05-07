import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QRect, QRectF
from PyQt5.QtGui import (QColor, QPixmap, QPainter, QPainterPath,
                          QBrush, QFont, QLinearGradient, QPen)


def _make_fullscreen_pixmap(user, size=300):
    """Retourne un QPixmap carré (photo réelle ou avatar)."""
    photo_path = user.get("photo_path")
    if photo_path and os.path.exists(photo_path):
        src = QPixmap(photo_path)
        if not src.isNull():
            # Crop carré + cercle
            pix = QPixmap(size, size)
            pix.fill(Qt.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            p.setClipPath(path)
            scaled = src.scaled(size, size, Qt.KeepAspectRatioByExpanding,
                                Qt.SmoothTransformation)
            ox = (scaled.width() - size) // 2
            oy = (scaled.height() - size) // 2
            p.drawPixmap(0, 0, scaled, ox, oy, size, size)
            p.setClipping(False)
            pen = QPen(QColor("#FFB300"), 5)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(3, 3, size - 6, size - 6)
            p.end()
            return pix

    # Fallback : avatar emoji sur fond dégradé
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    p.setClipPath(path)

    color = user.get("avatar_color", "#3498db")
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor(color).lighter(160))
    grad.setColorAt(1, QColor(color))
    p.fillRect(0, 0, size, size, QBrush(grad))

    p.setClipping(False)
    font = QFont("Segoe UI Emoji", size // 4)
    p.setFont(font)
    p.setPen(Qt.NoPen)
    p.drawText(QRect(0, 0, size, size), Qt.AlignCenter,
               user.get("avatar", "👤"))

    pen = QPen(QColor("#FFB300"), 5)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(3, 3, size - 6, size - 6)
    p.end()
    return pix


class FullscreenPhotoDialog(QDialog):
    """Affiche la photo de profil en plein écran sur fond sombre."""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet("background: #0A0A0A;")

        # Prendre toute la fenêtre parente
        if parent and parent.window():
            g = parent.window().geometry()
            self.setGeometry(g)
        else:
            self.setGeometry(100, 80, 430, 820)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Barre du haut avec bouton fermer ──────────────────────────────────
        top = QHBoxLayout()
        top.setContentsMargins(16, 16, 16, 0)
        top.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(44, 44)
        close_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.12); color: white;
                border: 1.5px solid rgba(255,255,255,0.25);
                border-radius: 22px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background: rgba(255,255,255,0.28); }
        """)
        close_btn.clicked.connect(self.close)
        top.addWidget(close_btn)
        layout.addLayout(top)
        layout.addStretch()

        # ── Photo circulaire ──────────────────────────────────────────────────
        avail = min(self.width(), self.height()) - 120
        size = max(220, min(avail, 340))
        pix = _make_fullscreen_pixmap(user, size)

        img_lbl = QLabel()
        img_lbl.setPixmap(pix)
        img_lbl.setFixedSize(size, size)
        img_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(img_lbl, alignment=Qt.AlignCenter)

        layout.addSpacing(24)

        # ── Nom ───────────────────────────────────────────────────────────────
        parts = [user.get("name", "")]
        if user.get("age"):
            parts.append(str(user["age"]))
        name_lbl = QLabel(" · ".join(parts))
        name_lbl.setStyleSheet(
            "color: white; font-size: 24px; font-weight: bold; background: transparent;")
        name_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_lbl)

        # ── École / Filière ───────────────────────────────────────────────────
        school = user.get("school", "")
        major  = user.get("major", "")
        if school or major:
            info_parts = []
            if school:
                info_parts.append(f"🏫 {school}")
            if major:
                info_parts.append(f"📖 {major}")
            info_lbl = QLabel("  ·  ".join(info_parts))
            info_lbl.setStyleSheet(
                "color: rgba(255,255,255,0.65); font-size: 14px; background: transparent;")
            info_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(info_lbl)

        layout.addStretch()

    def mousePressEvent(self, event):
        self.close()
