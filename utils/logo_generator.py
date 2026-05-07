"""
Génère le logo officiel UniShare (200×200px PNG).
Palette : Oxford Blue #192338 / Space Cadet #1E2E4F / YinMn Blue #31487A
          / Jordy Blue #8FB3E2 / Lavender #D9E1F1
"""
import os
import sys
from PyQt5.QtGui import (QPainter, QPixmap, QLinearGradient, QRadialGradient,
                          QColor, QPen, QFont, QPainterPath, QBrush)
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF

if getattr(sys, 'frozen', False):
    _ROOT = os.path.dirname(sys.executable)
else:
    _ROOT = os.path.dirname(os.path.dirname(__file__))

LOGO_PATH = os.path.join(_ROOT, "assests", "logo_unishare.png")

# ── Palette ──────────────────────────────────────────────────────────────────
C1 = QColor("#1E2E4F")   # Space Cadet  (fond haut)
C2 = QColor("#31487A")   # YinMn Blue   (fond bas)
C3 = QColor("#8FB3E2")   # Jordy Blue   (reflets)
C4 = QColor("#D9E1F1")   # Lavender     (halo / surbrillance)
GOLD  = QColor("#FFB300")
GOLD2 = QColor("#FFCA28")


def generate_logo(output_path=None):
    if output_path is None:
        output_path = LOGO_PATH

    S = 200
    pix = QPixmap(S, S)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)

    # ══════════════════════════════════════════════════════════════════════════
    # 1.  FOND — Space Cadet → YinMn Blue (diagonal, palette officielle)
    # ══════════════════════════════════════════════════════════════════════════
    bg = QPainterPath()
    bg.addRoundedRect(QRectF(0, 0, S, S), 44, 44)

    grd = QLinearGradient(0, 0, S, S)
    grd.setColorAt(0.0, C1)
    grd.setColorAt(1.0, C2)
    p.fillPath(bg, QBrush(grd))

    # Halo Jordy Blue clair centré (donne de la profondeur et éclaire)
    p.setClipPath(bg)
    hl = QRadialGradient(QPointF(S / 2, 90), S * 0.48)
    hl.setColorAt(0.0, QColor(143, 179, 226, 55))   # #8FB3E2 alpha 55
    hl.setColorAt(1.0, QColor(143, 179, 226, 0))
    p.fillRect(0, 0, S, S, QBrush(hl))

    # Bande sombre en bas pour le texte
    bot = QLinearGradient(0, 148, 0, S)
    bot.setColorAt(0.0, QColor(0, 0, 0, 0))
    bot.setColorAt(1.0, QColor(0, 0, 0, 150))
    p.fillRect(0, 148, S, S - 148, QBrush(bot))
    p.setClipping(False)

    # ══════════════════════════════════════════════════════════════════════════
    # 2.  CHAPEAU DE DIPLÔMÉ (gold)
    # ══════════════════════════════════════════════════════════════════════════
    cx, cy = S // 2, 40
    hw, hh = 36, 10

    # Plateau losange
    cap = QPainterPath()
    cap.moveTo(cx, cy - hh)
    cap.lineTo(cx + hw, cy)
    cap.lineTo(cx, cy + hh)
    cap.lineTo(cx - hw, cy)
    cap.closeSubpath()
    p.fillPath(cap, QBrush(GOLD))

    # Reflet clair sur le plateau
    shine = QPainterPath()
    shine.moveTo(cx, cy - hh)
    shine.lineTo(cx + hw, cy)
    shine.lineTo(cx, cy - 1)
    shine.lineTo(cx - hw, cy)
    shine.closeSubpath()
    p.fillPath(shine, QBrush(QColor(255, 255, 255, 50)))

    # Bouton central
    p.setBrush(QBrush(GOLD2))
    p.setPen(Qt.NoPen)
    p.drawEllipse(QRect(cx - 4, cy - 4, 8, 8))

    # Corps casquette
    body = QPainterPath()
    body.moveTo(cx - 20, cy + hh - 1)
    body.lineTo(cx - 12, cy + hh + 18)
    body.lineTo(cx + 12, cy + hh + 18)
    body.lineTo(cx + 20, cy + hh - 1)
    body.closeSubpath()
    p.fillPath(body, QBrush(GOLD.darker(118)))

    # Cordon + pompon
    pen_c = QPen(GOLD2, 2)
    pen_c.setCapStyle(Qt.RoundCap)
    p.setPen(pen_c)
    p.setBrush(Qt.NoBrush)
    p.drawLine(cx + hw - 2, cy, cx + hw + 4, cy + 20)
    p.setBrush(QBrush(GOLD2))
    p.setPen(Qt.NoPen)
    p.drawEllipse(QRect(cx + hw + 1, cy + 18, 7, 7))

    # ══════════════════════════════════════════════════════════════════════════
    # 3.  LETTRE « U » en PATH vectoriel — blanc + contour Jordy Blue
    # ══════════════════════════════════════════════════════════════════════════
    ux, uy = 50, 67
    uw, uh = 100, 78
    tw = 18

    u_path = QPainterPath()
    u_path.addRoundedRect(QRectF(ux, uy, tw, uh), 9, 9)
    u_path.addRoundedRect(QRectF(ux + uw - tw, uy, tw, uh), 9, 9)
    arc = QPainterPath()
    arc.addRoundedRect(QRectF(ux, uy + uh - tw * 2, uw, tw * 2 + 4), tw, tw)
    u_path = u_path.united(arc)

    # Ombre portée
    p.save()
    p.translate(2, 3)
    p.fillPath(u_path, QBrush(QColor(0, 0, 0, 90)))
    p.restore()

    # Remplissage blanc très lumineux
    p.fillPath(u_path, QBrush(QColor(255, 255, 255, 252)))

    # Contour Jordy Blue (#8FB3E2) pour harmonie palette
    pen_u = QPen(C3, 2.0)
    p.setPen(pen_u)
    p.setBrush(Qt.NoBrush)
    p.drawPath(u_path)

    # ══════════════════════════════════════════════════════════════════════════
    # 4.  NŒUDS DE RÉSEAU dans le bas du U
    # ══════════════════════════════════════════════════════════════════════════
    node_y = 152
    nodes  = [72, 100, 128]

    pen_l = QPen(QColor(255, 179, 0, 190), 1.8)
    pen_l.setCapStyle(Qt.RoundCap)
    p.setPen(pen_l)
    p.setBrush(Qt.NoBrush)
    for i in range(len(nodes) - 1):
        p.drawLine(nodes[i] + 5, node_y, nodes[i + 1] - 5, node_y)

    p.setPen(Qt.NoPen)
    for i, nx in enumerate(nodes):
        r = 6 if i == 1 else 5
        p.setBrush(QBrush(GOLD if i == 1 else GOLD2))
        p.drawEllipse(QRect(nx - r, node_y - r, r * 2, r * 2))

    # ══════════════════════════════════════════════════════════════════════════
    # 5.  TEXTE « Uni | Share »  sur bande sombre
    # ══════════════════════════════════════════════════════════════════════════
    ty, th = 165, 28
    font_t = QFont("Segoe UI", 13, QFont.Bold)
    p.setFont(font_t)

    # « Uni » en Lavender clair (#D9E1F1) — très lisible sur fond sombre
    p.setPen(QColor("#D9E1F1"))
    p.drawText(QRect(10, ty, 88, th), Qt.AlignRight | Qt.AlignVCenter, "Uni")

    # Séparateur
    p.setPen(QPen(QColor(255, 255, 255, 70), 1.2))
    p.drawLine(101, ty + 6, 101, ty + th - 6)

    # « Share » en or
    p.setPen(GOLD)
    p.drawText(QRect(104, ty, 86, th), Qt.AlignLeft | Qt.AlignVCenter, "Share")

    p.end()
    pix.save(output_path)
    return output_path


def get_logo_pixmap(size=36):
    from PyQt5.QtGui import QPixmap as QP
    if not os.path.exists(LOGO_PATH):
        generate_logo()
    pix = QP(LOGO_PATH)
    if pix.isNull():
        generate_logo()
        pix = QP(LOGO_PATH)
    return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def ensure_logo():
    if not os.path.exists(LOGO_PATH):
        generate_logo()
