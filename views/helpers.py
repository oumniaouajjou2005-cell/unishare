import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QPixmap, QPainter, QPainterPath, QBrush,
                          QLinearGradient, QPen, QColor, QFont)


def make_circle_pixmap(avatar_emoji="👤", avatar_color="#3498db", size=120, photo_path=None):
    """Crée un pixmap circulaire depuis une vraie photo ou un avatar emoji."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)

    clip = QPainterPath()
    clip.addEllipse(0, 0, size, size)
    p.setClipPath(clip)

    photo_drawn = False
    if photo_path and os.path.exists(photo_path):
        src = QPixmap(photo_path)
        if not src.isNull():
            src = src.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            ox = (src.width() - size) // 2
            oy = (src.height() - size) // 2
            p.drawPixmap(0, 0, src, ox, oy, size, size)
            photo_drawn = True

    if not photo_drawn:
        grad = QLinearGradient(0, 0, size, size)
        grad.setColorAt(0, QColor(avatar_color).lighter(150))
        grad.setColorAt(1, QColor(avatar_color))
        p.fillRect(0, 0, size, size, QBrush(grad))
        font = QFont()
        font.setPointSize(max(10, size // 4))
        p.setFont(font)
        p.setPen(Qt.NoPen)
        p.drawText(0, 0, size, size, Qt.AlignCenter, avatar_emoji)

    p.setClipping(False)
    p.setPen(QPen(QColor("#FFB300"), max(2, size // 40)))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(1, 1, size - 2, size - 2)
    p.end()
    return pix
