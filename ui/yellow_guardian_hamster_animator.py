"""
Yellow Guardian Hamster companion.

This is a completely separate companion from the White Meme Hamster.
It is a front-facing, upright, costume-based character inspired only by the
user-supplied reference: bright yellow body/robe, broad blue shoulder band,
black side sleeves, dark top cap/tuft, gray oval goggles, white face panel,
pink paws and tiny pink nose.
"""

import math

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath


class YellowGuardianHamsterAnimator:
    ONE_SHOT_DURATIONS = {
        "jump": 1.25,
        "wave": 1.10,
        "laugh": 1.50,
        "point": 1.15,
        "happy": 1.10,
        "react_click": 0.85,
    }

    def __init__(self, state_machine):
        self.state_machine = state_machine
        self.facing = 1
        self.elapsed = 0.0
        self._last_state = None

        self.outline = QColor(24, 24, 24)
        self.yellow = QColor(247, 207, 39)
        self.yellow_shadow = QColor(215, 174, 28)
        self.blue = QColor(37, 125, 222)
        self.blue_shadow = QColor(27, 84, 151)
        self.black = QColor(27, 30, 34)
        self.white = QColor(255, 255, 253)
        self.goggle = QColor(177, 173, 160)
        self.goggle_dark = QColor(111, 108, 100)
        self.pink = QColor(246, 161, 188)
        self.pink_dark = QColor(220, 114, 151)
        self.shadow = QColor(0, 0, 0, 42)

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def clear_special(self):
        self.elapsed = 0.0

    def reset_animation(self):
        self.elapsed = 0.0
        self._last_state = None

    def update(self):
        self.elapsed += 0.025
        state = self.state_machine.get_state()
        if state != self._last_state:
            self.elapsed = 0.0
            self._last_state = state
        duration = self.ONE_SHOT_DURATIONS.get(state)
        if duration is not None and self.elapsed >= duration:
            self.state_machine.force_state("idle")

    def _pen(self, width=2.0, color=None):
        return QPen(color or self.outline, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    def _path(self, points):
        p = QPainterPath()
        p.moveTo(*points[0])
        for pt in points[1:]:
            p.lineTo(*pt)
        p.closeSubpath()
        return p

    def _draw_shadow(self, painter, y_offset):
        w = 145.0 * max(0.6, 1.0 - min(abs(y_offset) / 90.0, 0.4))
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.shadow)
        painter.drawEllipse(QRectF(-w / 2, -4, w, 8))

    def _draw_outer_body(self, painter):
        # Distinct upright silhouette: broad yellow garment, narrower top,
        # rounded lower corners and flat-ish base, matching the reference.
        p = QPainterPath()
        p.moveTo(-42, -176)
        p.quadTo(-62, -159, -78, -132)
        p.quadTo(-94, -102, -101, -54)
        p.lineTo(-106, -8)
        p.quadTo(-104, 0, -92, 0)
        p.lineTo(92, 0)
        p.quadTo(104, 0, 106, -8)
        p.lineTo(101, -54)
        p.quadTo(94, -102, 78, -132)
        p.quadTo(62, -159, 42, -176)
        p.closeSubpath()
        painter.setBrush(self.yellow)
        painter.setPen(self._pen(2.2))
        painter.drawPath(p)

    def _draw_blue_shoulder_band(self, painter):
        # Large, asymmetric-looking blue band is a major silhouette cue.
        p = QPainterPath()
        p.moveTo(-83, -127)
        p.quadTo(-60, -106, -31, -94)
        p.quadTo(0, -83, 31, -94)
        p.quadTo(60, -106, 83, -127)
        p.lineTo(72, -96)
        p.quadTo(47, -77, 0, -68)
        p.quadTo(-47, -77, -72, -96)
        p.closeSubpath()
        painter.setBrush(self.blue)
        painter.setPen(self._pen(2.2, self.outline))
        painter.drawPath(p)

        painter.setPen(QPen(self.blue_shadow, 2.0))
        painter.drawArc(QRectF(-77, -118, 154, 58), 195 * 16, 150 * 16)
        painter.setPen(self._pen(2.0))

    def _draw_black_sleeves(self, painter, wave):
        painter.setBrush(self.black)
        painter.setPen(self._pen(2.0))

        left = QPainterPath()
        left.moveTo(-81, -119)
        left.quadTo(-98, -91, -101, -28)
        left.lineTo(-78, -17)
        left.lineTo(-62, -70)
        left.closeSubpath()
        painter.drawPath(left)

        right = QPainterPath()
        right.moveTo(81, -119)
        right.quadTo(98, -91, 101, -28)
        right.lineTo(78, -17)
        right.lineTo(62, -70)
        right.closeSubpath()
        painter.drawPath(right)

        # Small pink paws emerging at the sleeve ends.
        painter.setBrush(self.pink)
        painter.drawEllipse(QRectF(-92, -34 + wave, 18, 11))
        painter.drawEllipse(QRectF(74, -34 - wave, 18, 11))

    def _draw_center_panel(self, painter):
        # White central face opening and lower white chest inset.
        panel = QPainterPath()
        panel.moveTo(-36, -169)
        panel.lineTo(36, -169)
        panel.quadTo(47, -148, 45, -120)
        panel.lineTo(36, -85)
        panel.quadTo(0, -65, -36, -85)
        panel.lineTo(-45, -120)
        panel.quadTo(-47, -148, -36, -169)
        panel.closeSubpath()
        painter.setBrush(self.white)
        painter.setPen(self._pen(2.1))
        painter.drawPath(panel)

        chest = QRectF(-30, -86, 60, 86)
        painter.setBrush(self.yellow)
        painter.drawRoundedRect(chest, 10, 10)

    def _draw_head_cap(self, painter):
        # Dark top mass. Deliberately low and flattened, not a generic hat.
        p = QPainterPath()
        p.moveTo(-31, -175)
        p.quadTo(-23, -196, -2, -193)
        p.quadTo(15, -197, 29, -175)
        p.quadTo(21, -164, 0, -167)
        p.quadTo(-20, -164, -31, -175)
        p.closeSubpath()
        painter.setBrush(self.black)
        painter.setPen(self._pen(2.0))
        painter.drawPath(p)

    def _draw_goggles(self, painter, blink=0.0):
        # Two gray oval lenses sitting high on the white face panel.
        painter.setBrush(self.goggle)
        painter.setPen(self._pen(2.0, self.goggle_dark))
        painter.drawEllipse(QRectF(-45, -151, 39, 27))
        painter.drawEllipse(QRectF(6, -151, 39, 27))
        painter.drawLine(QPointF(-6, -138), QPointF(6, -138))

        # Soft highlight and dark lower edge give the exact flat printed look.
        painter.setPen(QPen(QColor(215, 212, 202), 1.4, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(QRectF(-41, -147, 31, 17), 180 * 16, 155 * 16)
        painter.drawArc(QRectF(10, -147, 31, 17), 180 * 16, 155 * 16)
        painter.setPen(self._pen(2.0))

    def _draw_face(self, painter, state):
        eye_y = -123
        if state == "laugh":
            painter.setPen(self._pen(2.5))
            for cx in (-21, 21):
                p = QPainterPath()
                p.moveTo(cx - 10, eye_y)
                p.quadTo(cx, eye_y - 8, cx + 10, eye_y)
                painter.drawPath(p)
        elif state == "sleep":
            painter.setPen(self._pen(2.4))
            painter.drawLine(QPointF(-31, eye_y), QPointF(-15, eye_y))
            painter.drawLine(QPointF(15, eye_y), QPointF(31, eye_y))
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.black)
            painter.drawEllipse(QRectF(-28, eye_y - 7, 13, 14))
            painter.drawEllipse(QRectF(15, eye_y - 7, 13, 14))
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-25, eye_y - 4, 4, 4))
            painter.drawEllipse(QRectF(18, eye_y - 4, 4, 4))

        # Pink nose.
        p = QPainterPath()
        p.moveTo(-8, -102)
        p.quadTo(0, -112, 8, -102)
        p.lineTo(0, -91)
        p.closeSubpath()
        painter.setBrush(self.pink)
        painter.setPen(self._pen(1.8))
        painter.drawPath(p)

        if state == "laugh":
            mouth = QPainterPath()
            mouth.moveTo(-15, -87)
            mouth.quadTo(0, -82, 15, -87)
            painter.setPen(self._pen(2.0))
            painter.drawPath(mouth)
        elif state == "happy":
            mouth = QPainterPath()
            mouth.moveTo(-13, -87)
            mouth.quadTo(0, -77, 13, -87)
            painter.setPen(self._pen(2.0))
            painter.drawPath(mouth)
        else:
            painter.setPen(QPen(self.outline, 1.8, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(-12, -84), QPointF(12, -84))

        # Subtle pink cheeks.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(246, 161, 188, 135))
        painter.drawEllipse(QRectF(-41, -103, 17, 7))
        painter.drawEllipse(QRectF(24, -103, 17, 7))

    def _draw_chest(self, painter):
        # Lower yellow panel with subtle center seam matching the graphic.
        painter.setBrush(self.yellow)
        painter.setPen(self._pen(2.0))
        painter.drawRoundedRect(QRectF(-30, -86, 60, 86), 11, 11)
        painter.setPen(QPen(self.yellow_shadow, 1.1))
        painter.drawLine(QPointF(0, -80), QPointF(0, -10))
        painter.setPen(self._pen(2.0))

    def draw(self, painter, rect):
        state = self.state_machine.get_state()
        t = self.elapsed

        y_offset = 0.0
        scale_x = 1.0
        scale_y = 1.0
        rotation = 0.0
        wave = 0.0

        if state in ("jump", "celebrate"):
            phase = min(1.0, t / 1.25)
            y_offset = -58 * math.sin(phase * math.pi)
            scale_x = 0.92 if phase < 0.7 else 1.08
            scale_y = 1.08 if phase < 0.7 else 0.92
            rotation = math.sin(phase * math.pi * 2.0) * 4.0
        elif state == "wave":
            wave = math.sin(t * 14.0) * 8.0
        elif state == "wander":
            y_offset = -abs(math.sin(t * 5.0)) * 2.0
        elif state == "sleep":
            scale_y = 0.96
            y_offset = 3.0
        else:
            y_offset = math.sin(t * 2.5) * 1.2

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(rect.center().x(), rect.bottom())
        painter.scale(self.facing, 1.0)

        self._draw_shadow(painter, y_offset)
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)
        painter.rotate(rotation)

        self._draw_outer_body(painter)
        self._draw_black_sleeves(painter, wave)
        self._draw_blue_shoulder_band(painter)
        self._draw_center_panel(painter)
        self._draw_chest(painter)
        self._draw_head_cap(painter)
        self._draw_goggles(painter)

        face_state = "laugh" if state == "laugh" else "sleep" if state == "sleep" else "happy" if state in ("happy", "celebrate", "react_click") else "neutral"
        self._draw_face(painter, face_state)

        if state == "wave":
            painter.setBrush(self.pink)
            painter.setPen(self._pen(1.4))
            painter.drawEllipse(QRectF(-103, -76 + wave, 18, 11))

        if state == "point":
            painter.setPen(self._pen(2.0))
            painter.drawLine(QPointF(79, -45), QPointF(112, -58))
            painter.setBrush(self.pink)
            painter.setPen(self._pen(1.4))
            painter.drawEllipse(QRectF(105, -64, 12, 10))

        painter.restore()
