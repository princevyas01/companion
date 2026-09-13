"""Exact source-sprite renderer for the user's White Meme Hamster.

The character artwork itself is never procedurally redrawn. The renderer loads
the clean hand-drawn source frames and animates the complete image.
"""
import math
import sys
from collections import deque
from pathlib import Path

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPixmap, QColor


class WhiteHamsterAnimator:
    """Exact source-sprite animation. No procedural facial reconstruction."""

    ONE_SHOT_DURATIONS = {
        "laugh": 2.25,
        "smile": 2.25,
        "neutral": 2.25,
        "tongue_out": 2.25,
        "halo": 3.25,
        "costume": 3.25,
        "jump": 1.20,
        "celebrate": 2.25,
        "react_click": 1.60,
        "happy": 2.25,
        "think": 2.25,
        "annoyed": 2.25,
        "focus": 2.25,
        "type": 2.25,
        "sleep": 2.25,
        "wake": 1.40,
    }

    FRAME_FILES = {
        "laugh": "laugh.png",
        "smile": "smile.png",
        "neutral": "neutral.png",
        "tongue_out": "tongue_out.png",
        "halo": "halo.png",
        "costume": "costume.png",
    }

    DEFAULT_EXPRESSION = "laugh"

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
        # Compatibility with the existing wander engine.
        # The hand-drawn source is intentionally asymmetric and is never mirrored.
        self.facing = 1 if direction >= 0 else -1

    def clear_special(self):
        self.elapsed = 0.0
        self._last_state = None

    def reset_animation(self):
        self.elapsed = 0.0
        self._last_state = None

    @staticmethod
    def _near_white(pixel: QColor):
        return (
            pixel.alpha() > 0
            and pixel.red() >= 242
            and pixel.green() >= 242
            and pixel.blue() >= 242
        )

    @classmethod
    def _remove_connected_white_background(cls, image: QImage):
        """Remove only near-white pixels connected to the outer border."""
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
            if not cls._near_white(image.pixelColor(x, y)):
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
                    image.setPixelColor(x, y, QColor(0, 0, 0, 0))

        left, top = w, h
        right, bottom = -1, -1

        for y in range(h):
            for x in range(w):
                if image.pixelColor(x, y).alpha() > 0:
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
                "White Meme Hamster reference assets missing:\n"
                + "\n".join(missing)
            )

    def _expression_for_state(self, state):
        # DEFAULT IS THE HUMOROUS LAUGH SOURCE.
        if state in (
            "idle",
            "wake",
            "wander",
            "laugh",
            "celebrate",
            "react_click",
            "happy",
        ):
            return "laugh"

        if state == "jump":
            return "laugh"

        if state in (
            "neutral",
            "think",
            "annoyed",
            "exhausted",
            "focus",
            "type",
            "sleep",
        ):
            return "neutral"

        if state == "tongue_out":
            return "tongue_out"

        if state == "halo":
            return "halo"

        if state == "costume":
            return "costume"

        return self.DEFAULT_EXPRESSION

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

    def draw(self, painter, rect):
        state = self.state_machine.get_state()
        expression = self._expression_for_state(state)
        pixmap = self.frames.get(expression) or self.frames[self.DEFAULT_EXPRESSION]

        y_offset = 0.0
        sx = 1.0
        sy = 1.0

        if state in ("jump", "celebrate"):
            duration = 1.20 if state == "jump" else 2.25
            p = max(0.0, min(1.0, self.elapsed / duration))
            y_offset = -48.0 * math.sin(p * math.pi)

            if p < 0.14:
                u = p / 0.14
                sx = 1.0 + 0.045 * (1.0 - u)
                sy = 1.0 - 0.035 * (1.0 - u)
            elif p > 0.86:
                u = (p - 0.86) / 0.14
                sx = 1.0 + 0.05 * u
                sy = 1.0 - 0.04 * u
            else:
                sx = 0.985
                sy = 1.015

        elif state == "wander":
            phase = self.elapsed * 5.0
            y_offset = -abs(math.sin(phase)) * 2.0

        elif state in ("halo", "costume"):
            y_offset = math.sin(self.elapsed * 2.0) * 0.7

        elif state == "sleep":
            y_offset = 2.0

        painter.save()

        # NEVER mirror the actual hand-drawn artwork.
        painter.translate(rect.center().x(), rect.bottom() - 2.0)
        painter.translate(0.0, y_offset)
        painter.scale(sx, sy)

        # The source must remain inside the normal pet rectangle.
        max_h = max(120.0, float(rect.height()) - 4.0)
        target_h = min(160.0, max_h)

        scaled = pixmap.scaledToHeight(
            max(1, int(round(target_h))),
            Qt.FastTransformation,
        )

        painter.drawPixmap(
            int(-scaled.width() / 2),
            -scaled.height(),
            scaled,
        )

        painter.restore()
