"""
Exact reference-sprite renderer for the user's White Meme Hamster.

This renderer deliberately does NOT redraw the character with QPainter geometry.
It uses the six user-supplied reference drawings as the visual source of truth,
removing only the outside white background while preserving the enclosed white
body pixels and every original imperfection.
"""
import math
import sys
from collections import deque
from pathlib import Path

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor


class WhiteHamsterAnimator:
    """Reference-sprite animator. Facial art is never recreated procedurally."""

    ONE_SHOT_DURATIONS = {
        "laugh": 1.80,
        "smile": 1.50,
        "neutral": 1.50,
        "tongue_out": 1.80,
        "halo": 2.80,
        "costume": 4.50,
        "jump": 1.15,
        "celebrate": 1.80,
        "react_click": 1.20,
    }

    FRAME_FILES = {
        "laugh": "laugh.png",
        "smile": "smile.png",
        "neutral": "neutral.png",
        "tongue_out": "tongue_out.png",
        "halo": "halo.png",
        "costume": "costume.png",
    }

    def __init__(self, state_machine, asset_dir=None):
        self.state_machine = state_machine
        self.facing = 1
        self.elapsed = 0.0
        self._last_state = None

        default_dir = Path(__file__).resolve().parents[1] / "assets" / "white_hamster"
        if hasattr(sys, "_MEIPASS"):
            meipass_dir = Path(sys._MEIPASS) / "assets" / "white_hamster"
            if meipass_dir.exists():
                default_dir = meipass_dir
        self.asset_dir = Path(asset_dir) if asset_dir else default_dir
        self.frames = {}
        self._load_frames()

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def clear_special(self):
        self.elapsed = 0.0
        self._last_state = None

    def reset_animation(self):
        self.elapsed = 0.0
        self._last_state = None

    @staticmethod
    def _near_white(pixel: QColor):
        # Only treat very light pixels as removable background.
        # This is intentionally conservative so pink cheeks and anti-aliased
        # dark linework are not destroyed.
        return pixel.alpha() > 0 and pixel.red() >= 242 and pixel.green() >= 242 and pixel.blue() >= 242

    @classmethod
    def _remove_connected_white_background(cls, image: QImage):
        """Remove only near-white pixels connected to the image border.

        The hamster's white body is enclosed by its dark hand-drawn outline, so
        enclosed white pixels remain opaque. This preserves the white character
        while removing the screenshot/background rectangle.
        """
        image = image.convertToFormat(QImage.Format_ARGB32)
        w, h = image.width(), image.height()
        if w <= 0 or h <= 0:
            return image

        removable = bytearray(w * h)
        queue = deque()

        def idx(x, y):
            return y * w + x

        def visit(x, y):
            i = idx(x, y)
            if removable[i]:
                return
            if not cls._near_white(QColor(image.pixel(x, y))):
                return
            removable[i] = 1
            queue.append((x, y))

        for x in range(w):
            visit(x, 0)
            if h > 1:
                visit(x, h - 1)
        for y in range(h):
            visit(0, y)
            if w > 1:
                visit(w - 1, y)

        while queue:
            x, y = queue.popleft()
            if x > 0:
                visit(x - 1, y)
            if x + 1 < w:
                visit(x + 1, y)
            if y > 0:
                visit(x, y - 1)
            if y + 1 < h:
                visit(x, y + 1)

        for y in range(h):
            for x in range(w):
                if removable[idx(x, y)]:
                    image.setPixelColor(x, y, QColor(255, 255, 255, 0))

        # Trim transparent-only margins. This does not alter opaque pixels.
        bbox = image.convertToFormat(QImage.Format_ARGB32).mirrored(False, False)
        left, top = w, h
        right, bottom = -1, -1
        for y in range(h):
            for x in range(w):
                if QColor(bbox.pixel(x, y)).alpha() > 0:
                    left = min(left, x)
                    top = min(top, y)
                    right = max(right, x)
                    bottom = max(bottom, y)
        if right < left or bottom < top:
            return image
        return image.copy(left, top, right - left + 1, bottom - top + 1)

    def _load_frames(self):
        missing = []
        for state, filename in self.FRAME_FILES.items():
            path = self.asset_dir / filename
            image = QImage(str(path))
            if image.isNull():
                missing.append(str(path))
                continue
            cleaned = self._remove_connected_white_background(image)
            self.frames[state] = QPixmap.fromImage(cleaned, Qt.AutoColor)
        if missing:
            raise FileNotFoundError(
                "White Meme Hamster reference assets missing:\n" + "\n".join(missing)
            )

    def _expression_for_state(self, state):
        if state in ("laugh", "celebrate", "react_click"):
            return "laugh"
        if state == "jump":
            return "laugh"
        if state in ("neutral", "think", "annoyed", "exhausted", "focus", "type", "sleep"):
            return "neutral"
        if state == "tongue_out":
            return "tongue_out"
        if state == "halo":
            return "halo"
        if state in ("costume",):
            return "costume"
        return "smile"

    def update(self):
        state = self.state_machine.get_state()
        dt = 0.025
        if state != self._last_state:
            self.elapsed = 0.0
            self._last_state = state
        else:
            self.elapsed += dt

        duration = self.ONE_SHOT_DURATIONS.get(state)
        if duration is not None and self.elapsed >= duration:
            self.state_machine.force_state("idle")
            self.elapsed = 0.0
            self._last_state = "idle"

    def _draw_shadow(self, painter, y_offset):
        width = 150.0 * max(0.55, 1.0 - min(abs(y_offset) / 90.0, 0.50))
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 42))
        painter.drawEllipse(QRectF(-width / 2, -3.5, width, 7))
        painter.restore()

    def draw(self, painter, rect):
        state = self.state_machine.get_state()
        expression = self._expression_for_state(state)
        pixmap = self.frames.get(expression) or self.frames["smile"]

        y_offset = 0.0
        sx = 1.0
        sy = 1.0
        rotation = 0.0

        if state in ("jump", "celebrate"):
            duration = 1.15 if state == "jump" else 1.80
            p = max(0.0, min(1.0, self.elapsed / duration))
            y_offset = -62.0 * math.sin(p * math.pi)
            if p < 0.16:
                u = p / 0.16
                sx = 1.0 + 0.10 * (1.0 - u)
                sy = 1.0 - 0.12 * (1.0 - u)
            elif p > 0.84:
                u = (p - 0.84) / 0.16
                sx = 1.0 + 0.14 * u
                sy = 1.0 - 0.12 * u
            else:
                sx = 0.93
                sy = 1.08
            rotation = math.sin(p * math.pi * 2.0) * 3.0
        elif state == "wander":
            phase = self.elapsed * 5.5
            y_offset = -abs(math.sin(phase)) * 3.0
            rotation = math.sin(phase) * 1.5
        elif state in ("focus", "type", "costume"):
            y_offset = math.sin(self.elapsed * 2.5) * 1.0
        elif state == "sleep":
            sy = 0.97
            sx = 1.04
            y_offset = 3.0

        painter.save()
        # Deliberately do NOT enable antialiasing or SmoothPixmapTransform.
        # The source artwork is hand-drawn/low-resolution and its imperfections
        # are part of the design.
        painter.translate(rect.center().x(), rect.bottom())
        painter.scale(self.facing, 1.0)
        self._draw_shadow(painter, y_offset)
        painter.translate(0.0, y_offset)
        painter.rotate(rotation)
        painter.scale(sx, sy)

        target_h = min(float(rect.height()) * 0.78, 300.0)
        scaled = pixmap.scaledToHeight(max(1, int(target_h)), Qt.FastTransformation)
        painter.drawPixmap(
            int(-scaled.width() / 2),
            -scaled.height(),
            scaled,
        )
        painter.restore()

