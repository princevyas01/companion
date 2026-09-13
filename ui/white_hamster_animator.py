"""
White Meme Hamster companion renderer.

Reference-driven original QPainter implementation for the user-supplied
white hamster character references.

Design target:
- Pure white, almost paper-white, soft blob/triangular hamster silhouette.
- Flat-ish narrow top that expands into very broad rounded lower sides.
- Minimal black sketch linework.
- Small dark scribbly eyes.
- Pink triangular nose and soft pink cheek blush.
- Expression states reproduce the supplied reference moods:
  smile, laugh, neutral, tongue-out, halo, costume, jump.
- Final costume state reproduces the supplied yellow/blue/black outfit,
  dark cap/hair tuft and gray oval glasses/goggles.
- No brown fur, orange fur, ordinary hamster ears, or generic rodent anatomy.
"""

import math

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath


class WhiteHamsterAnimator:
    """Procedural QPainter animator for the supplied white hamster character."""

    ONE_SHOT_DURATIONS = {
        "laugh": 1.8,
        "smile": 1.5,
        "neutral": 1.5,
        "tongue_out": 1.8,
        "halo": 2.8,
        "costume": 4.5,
        "jump": 1.15,
        "celebrate": 1.8,
        "react_click": 1.2,
    }

    def __init__(self, state_machine):
        self.state_machine = state_machine
        self.facing = 1
        self.elapsed = 0.0
        self._last_state = None

        # Reference palette.
        self.white = QColor(255, 255, 252)
        self.black = QColor(18, 18, 18)
        self.soft_black = QColor(36, 36, 36)
        self.gray = QColor(120, 120, 120)
        self.pink = QColor(244, 157, 181)
        self.pink_light = QColor(248, 190, 207)
        self.pink_deep = QColor(223, 111, 147)
        self.yellow = QColor(244, 206, 44)
        self.yellow_dark = QColor(207, 167, 30)
        self.blue = QColor(48, 132, 224)
        self.blue_dark = QColor(27, 85, 153)
        self.costume_black = QColor(28, 31, 34)
        self.shadow = QColor(0, 0, 0, 38)

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def clear_special(self):
        # StateMachine remains authoritative.
        self.elapsed = 0.0

    def reset_animation(self):
        self.elapsed = 0.0
        self._last_state = None

    def update(self):
        dt = 0.025
        self.elapsed += dt

        state = self.state_machine.get_state()
        if state != self._last_state:
            self.elapsed = 0.0
            self._last_state = state

        # One-shot visual states return to idle automatically.
        duration = self.ONE_SHOT_DURATIONS.get(state)
        if duration is not None and self.elapsed >= duration:
            self.state_machine.force_state("idle")

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _pen(self, width=2.2, color=None):
        return QPen(
            color or self.black,
            width,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin,
        )

    def _body_path(self, painter):
        """Draw the signature white tapered/triangular hamster silhouette."""
        p = QPainterPath()
        p.moveTo(-18, -178)
        p.lineTo(18, -178)

        p.cubicTo(40, -176, 47, -166, 57, -150)
        p.cubicTo(69, -134, 84, -119, 94, -99)
        p.cubicTo(105, -77, 111, -50, 112, -20)
        p.cubicTo(113, -7, 108, 0, 96, 0)

        p.lineTo(-96, 0)
        p.cubicTo(-108, 0, -113, -7, -112, -20)
        p.cubicTo(-111, -50, -105, -77, -94, -99)
        p.cubicTo(-84, -119, -69, -134, -57, -150)
        p.cubicTo(-47, -166, -40, -176, -18, -178)
        p.closeSubpath()

        painter.setBrush(self.white)
        painter.setPen(self._pen(2.2))
        painter.drawPath(p)

    def _draw_ground_shadow(self, painter, y_offset):
        width = 155.0 * max(0.55, 1.0 - min(abs(y_offset) / 80.0, 0.45))
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.shadow)
        painter.drawEllipse(QRectF(-width / 2.0, -3, width, 7))

    def _draw_scribble_eye(self, painter, cx, cy, scale=1.0):
        """Dense black irregular eye matching the low-resolution source art."""
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.black)
        painter.drawEllipse(
            QRectF(cx - 10 * scale, cy - 9 * scale, 20 * scale, 18 * scale)
        )
        painter.setPen(QPen(QColor(255, 255, 255, 70), max(1.0, scale)))
        painter.drawArc(
            QRectF(cx - 8 * scale, cy - 7 * scale, 14 * scale, 13 * scale),
            10 * 16,
            190 * 16,
        )
        painter.drawArc(
            QRectF(cx - 5 * scale, cy - 5 * scale, 13 * scale, 11 * scale),
            188 * 16,
            155 * 16,
        )
        painter.setPen(self._pen(2.2))

    def _draw_open_eyes(self, painter):
        self._draw_scribble_eye(painter, -34, -132, 1.0)
        self._draw_scribble_eye(painter, 34, -132, 1.0)

    def _draw_closed_happy_eyes(self, painter):
        painter.setPen(self._pen(2.6))
        left = QPainterPath()
        left.moveTo(-49, -129)
        left.quadTo(-39, -141, -29, -129)
        painter.drawPath(left)

        right = QPainterPath()
        right.moveTo(29, -129)
        right.quadTo(39, -141, 49, -129)
        painter.drawPath(right)

    def _draw_nose(self, painter):
        p = QPainterPath()
        p.moveTo(-8, -108)
        p.quadTo(0, -118, 8, -108)
        p.lineTo(0, -94)
        p.closeSubpath()

        painter.setBrush(self.pink)
        painter.setPen(self._pen(1.8, self.black))
        painter.drawPath(p)

    def _draw_blush(self, painter, strong=False):
        alpha = 205 if strong else 145
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self.pink.red(), self.pink.green(), self.pink.blue(), alpha))
        painter.drawEllipse(QRectF(-70, -112, 22, 10))
        painter.drawEllipse(QRectF(48, -112, 22, 10))

        # Characteristic diagonal sketch strokes visible in the references.
        painter.setPen(QPen(QColor(223, 120, 150, 150), 1.2, Qt.SolidLine, Qt.RoundCap))
        for side in (-1, 1):
            x = -68 if side < 0 else 54
            for i in range(3):
                painter.drawLine(
                    QPointF(x + i * 4, -115 + i * 1.5),
                    QPointF(x + 5 + i * 4, -109 + i * 1.5),
                )
        painter.setPen(self._pen(2.2))

    def _draw_smile(self, painter):
        # Small closed smile and pink lower lip/inner mouth.
        p = QPainterPath()
        p.moveTo(-24, -82)
        p.quadTo(-11, -69, 0, -70)
        p.quadTo(11, -69, 24, -82)
        painter.setPen(self._pen(2.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(p)

        painter.setPen(QPen(self.pink_deep, 2.2))
        painter.drawArc(QRectF(-12, -68, 24, 11), 190 * 16, 160 * 16)
        painter.setPen(self._pen(2.2))

    def _draw_neutral(self, painter):
        # Reference 3: tiny horizontal, slightly sad/flat mouth.
        painter.setPen(QPen(self.soft_black, 2.3, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(-23, -78), QPointF(23, -78))
        painter.setPen(QPen(self.pink_deep, 1.5, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(-14, -74), QPointF(14, -74))
        painter.setPen(self._pen(2.2))

    def _draw_laugh(self, painter):
        # Reference 1: huge black open laugh, two large upper incisors,
        # pink lower mouth/tongue edge.
        p = QPainterPath()
        p.moveTo(-47, -83)
        p.quadTo(-22, -91, 0, -88)
        p.quadTo(22, -91, 47, -83)
        p.cubicTo(49, -54, 34, -31, 0, -29)
        p.cubicTo(-34, -31, -49, -54, -47, -83)
        p.closeSubpath()

        painter.setBrush(self.black)
        painter.setPen(self._pen(2.3))
        painter.drawPath(p)

        # Two unmistakable rabbit-like hamster incisors from reference.
        painter.setBrush(self.white)
        painter.setPen(self._pen(1.4, self.soft_black))
        painter.drawRect(QRectF(-8, -85, 7, 21))
        painter.drawRect(QRectF(1, -85, 7, 21))

        # Pink lower inner mouth / tongue.
        painter.setBrush(self.pink_light)
        painter.setPen(self._pen(1.5, self.soft_black))
        painter.drawEllipse(QRectF(-16, -46, 32, 13))

        painter.setPen(QPen(self.pink_deep, 1.5))
        painter.drawArc(QRectF(-12, -41, 24, 8), 180 * 16, 180 * 16)
        painter.setPen(self._pen(2.2))

    def _draw_tongue_out(self, painter):
        # Reference 4: open black mouth with a conspicuous round pink tongue.
        painter.setBrush(self.black)
        painter.setPen(self._pen(2.0))
        painter.drawPath(self._rounded_mouth_path(-43, -82, 86, 35))

        painter.setBrush(self.pink_light)
        painter.setPen(self._pen(1.8, self.soft_black))
        painter.drawEllipse(QRectF(-16, -58, 32, 29))

        painter.setPen(QPen(self.pink_deep, 1.5))
        painter.drawLine(QPointF(0, -54), QPointF(0, -38))
        painter.setPen(self._pen(2.2))

    def _rounded_mouth_path(self, x, y, w, h):
        p = QPainterPath()
        p.moveTo(x + 8, y)
        p.quadTo(x + w / 2.0, y + 8, x + w - 8, y)
        p.quadTo(x + w, y + h * 0.15, x + w - 6, y + h * 0.65)
        p.quadTo(x + w / 2.0, y + h, x + 6, y + h * 0.65)
        p.quadTo(x, y + h * 0.15, x + 8, y)
        p.closeSubpath()
        return p

    def _draw_hands(self, painter, together=False):
        painter.setPen(self._pen(2.0))
        painter.setBrush(Qt.NoBrush)

        if together:
            # Reference 5: tiny paws/arms meeting in front of the lower face.
            left = QPainterPath()
            left.moveTo(-30, -35)
            left.quadTo(-20, -45, -8, -29)
            painter.drawPath(left)

            right = QPainterPath()
            right.moveTo(30, -35)
            right.quadTo(20, -45, 8, -29)
            painter.drawPath(right)

            painter.drawLine(QPointF(-7, -29), QPointF(0, -24))
            painter.drawLine(QPointF(7, -29), QPointF(0, -24))
        else:
            # Tiny signature front-paw strokes from the references.
            painter.drawLine(QPointF(-25, -26), QPointF(-17, -21))
            painter.drawLine(QPointF(18, -22), QPointF(26, -27))

    def _draw_halo(self, painter):
        painter.setPen(QPen(self.yellow, 4.0, Qt.SolidLine, Qt.RoundCap))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(-28, -208, 56, 17))
        painter.setPen(self._pen(2.2))

    def _draw_costume(self, painter):
        """
        Reference 6 costume:
        yellow robe/body shell, strong blue shoulder/collar band, black sleeves,
        dark top tuft/cap, gray oval glasses.
        """
        # Yellow outer garment.
        garment = QPainterPath()
        garment.moveTo(-91, -124)
        garment.quadTo(-74, -150, -42, -164)
        garment.lineTo(42, -164)
        garment.quadTo(74, -150, 91, -124)
        garment.lineTo(105, -7)
        garment.quadTo(102, 0, 92, 0)
        garment.lineTo(-92, 0)
        garment.quadTo(-102, 0, -105, -7)
        garment.closeSubpath()

        painter.setBrush(self.yellow)
        painter.setPen(self._pen(2.4, self.soft_black))
        painter.drawPath(garment)

        # Black side sleeves.
        painter.setBrush(self.costume_black)
        left = QPainterPath()
        left.moveTo(-92, -118)
        left.quadTo(-107, -90, -109, -30)
        left.lineTo(-80, -18)
        left.lineTo(-65, -73)
        left.closeSubpath()
        painter.drawPath(left)

        right = QPainterPath()
        right.moveTo(92, -118)
        right.quadTo(107, -90, 109, -30)
        right.lineTo(80, -18)
        right.lineTo(65, -73)
        right.closeSubpath()
        painter.drawPath(right)

        # Blue shoulder/scarf band.
        band = QPainterPath()
        band.moveTo(-86, -121)
        band.quadTo(-61, -98, -27, -88)
        band.lineTo(0, -83)
        band.lineTo(27, -88)
        band.quadTo(61, -98, 86, -121)
        band.lineTo(75, -92)
        band.quadTo(45, -73, 0, -68)
        band.quadTo(-45, -73, -75, -92)
        band.closeSubpath()
        painter.setBrush(self.blue)
        painter.setPen(self._pen(2.0, self.soft_black))
        painter.drawPath(band)

        # Yellow center panel over the band.
        painter.setBrush(self.yellow)
        painter.drawRoundedRect(QRectF(-30, -88, 60, 88), 12, 12)

        # Dark top tuft/cap.
        painter.setBrush(self.costume_black)
        tuft = QPainterPath()
        tuft.moveTo(-31, -171)
        tuft.quadTo(-20, -193, 0, -188)
        tuft.quadTo(21, -194, 31, -169)
        tuft.quadTo(23, -159, 0, -164)
        tuft.quadTo(-23, -159, -31, -171)
        tuft.closeSubpath()
        painter.drawPath(tuft)

        # Two gray oval goggles.
        painter.setBrush(QColor(178, 174, 160))
        painter.setPen(self._pen(2.0, self.soft_black))
        painter.drawEllipse(QRectF(-45, -150, 40, 25))
        painter.drawEllipse(QRectF(5, -150, 40, 25))

        # Goggle bridge.
        painter.drawLine(QPointF(-5, -139), QPointF(5, -139))

        # Restore visible white face opening on top of costume.
        face = QPainterPath()
        face.moveTo(-34, -155)
        face.lineTo(34, -155)
        face.quadTo(48, -136, 43, -100)
        face.lineTo(32, -67)
        face.quadTo(0, -52, -32, -67)
        face.lineTo(-43, -100)
        face.quadTo(-48, -136, -34, -155)
        face.closeSubpath()
        painter.setBrush(self.white)
        painter.setPen(self._pen(2.0, self.soft_black))
        painter.drawPath(face)

    # ------------------------------------------------------------------
    # Main rendering
    # ------------------------------------------------------------------

    def draw(self, painter, rect):
        state = self.state_machine.get_state()
        t = self.elapsed

        # Normalize expressions for generic app states.
        if state in ("idle", "wander", "wake"):
            expression = "smile"
        elif state in ("laugh", "celebrate", "jump", "react_click"):
            expression = "laugh"
        elif state in ("neutral", "annoyed", "exhausted"):
            expression = "neutral"
        elif state == "tongue_out":
            expression = "tongue_out"
        elif state == "halo":
            expression = "halo"
        elif state in ("costume", "focus", "type"):
            expression = "costume"
        elif state == "think":
            expression = "neutral"
        elif state == "sleep":
            expression = "sleep"
        else:
            expression = "smile"

        # Kinematics.
        y_offset = 0.0
        scale_x = 1.0
        scale_y = 1.0
        rotation = 0.0

        if state in ("jump", "celebrate"):
            cycle = min(1.0, t / (1.15 if state == "jump" else 1.8))
            y_offset = -62.0 * math.sin(cycle * math.pi)
            if cycle < 0.16:
                scale_x = 1.10
                scale_y = 0.88
            elif cycle > 0.84:
                squash = (cycle - 0.84) / 0.16
                scale_x = 1.0 + 0.15 * squash
                scale_y = 1.0 - 0.14 * squash
            else:
                scale_x = 0.92
                scale_y = 1.08
            rotation = math.sin(cycle * math.pi * 2.0) * 3.0

        elif state == "wander":
            phase = t * 5.5
            y_offset = -abs(math.sin(phase)) * 3.0
            rotation = math.sin(phase) * 2.5

        elif state in ("focus", "type", "costume"):
            y_offset = math.sin(t * 2.5) * 1.2

        elif state == "sleep":
            y_offset = 3.5
            scale_x = 1.05
            scale_y = 0.96

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(rect.center().x(), rect.bottom())
        painter.scale(self.facing, 1.0)

        self._draw_ground_shadow(painter, y_offset)
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)
        painter.rotate(rotation)

        # Base character silhouette.
        self._body_path(painter)

        # Costume overlays the body but keeps a clearly white face.
        if expression == "costume":
            self._draw_costume(painter)

        # Facial layer.
        if expression == "laugh":
            self._draw_closed_happy_eyes(painter)
            self._draw_blush(painter, strong=True)
            self._draw_nose(painter)
            self._draw_laugh(painter)
        elif expression == "neutral":
            self._draw_open_eyes(painter)
            self._draw_blush(painter, strong=False)
            self._draw_nose(painter)
            self._draw_neutral(painter)
        elif expression == "tongue_out":
            self._draw_open_eyes(painter)
            self._draw_blush(painter, strong=True)
            self._draw_nose(painter)
            self._draw_tongue_out(painter)
        elif expression == "halo":
            self._draw_closed_happy_eyes(painter)
            self._draw_blush(painter, strong=True)
            self._draw_nose(painter)
            self._draw_smile(painter)
            self._draw_hands(painter, together=True)
            self._draw_halo(painter)
        elif expression == "costume":
            # The costume reference has sleepy/closed oval goggles above the face.
            painter.save()
            # Small simple face inside the white face panel.
            self._draw_scribble_eye(painter, -22, -123, 0.72)
            self._draw_scribble_eye(painter, 22, -123, 0.72)
            self._draw_blush(painter, strong=False)
            self._draw_nose(painter)
            self._draw_neutral(painter)
            painter.restore()
        elif expression == "sleep":
            self._draw_closed_happy_eyes(painter)
            self._draw_nose(painter)
            self._draw_smile(painter)
        else:
            self._draw_open_eyes(painter)
            self._draw_blush(painter, strong=False)
            self._draw_nose(painter)
            self._draw_smile(painter)

        painter.restore()
